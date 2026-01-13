import os
import re
import oss2
import urllib.parse
import mimetypes
from flask import Flask, render_template, request, jsonify, Response
from .config_manager import AppConfig

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

app = Flask(__name__)

# Inject version into all templates
@app.context_processor
def inject_version():
    return dict(version=__version__)

# Initialize Config
cfg = AppConfig()

def get_oss_url_pattern():
    domain = cfg.get("OSS_DOMAIN")
    prefix = cfg.get("PREFIX")
    
    if not prefix:
        raise ValueError("请先配置 PREFIX")

    if not domain:
        # 如果没有配置自定义域名，则使用默认域名: bucket.endpoint
        bucket = cfg.get("BUCKET_NAME")
        endpoint = cfg.get("ENDPOINT")
        if bucket and endpoint:
            # 去除 endpoint 可能包含的协议头
            clean_endpoint = endpoint.replace("http://", "").replace("https://", "")
            domain = f"{bucket}.{clean_endpoint}"
        else:
             raise ValueError("请配置 OSS_DOMAIN 或完整的 Bucket/Endpoint 信息")

    # Support both http and https
    return re.compile(
        rf'https?://{domain}/{prefix}([^\)\s\?]+)')


def create_oss_bucket(ak_id, ak_secret, endpoint, bucket_name, oss_domain=None):
    """Helper to create OSS Bucket instance with consistent logic."""
    if not all([ak_id, ak_secret, endpoint, bucket_name]):
        raise ValueError("请先在配置页面设置 OSS 相关信息 (Access Key, Endpoint, Bucket)")

    auth = oss2.Auth(ak_id, ak_secret)
    
    # 如果配置了自定义域名，优先使用自定义域名 (CNAME)
    if oss_domain:
        if not oss_domain.startswith('http'):
            oss_domain = 'https://' + oss_domain
        elif oss_domain.startswith('http://'):
            oss_domain = oss_domain.replace('http://', 'https://', 1)
        return oss2.Bucket(auth, oss_domain, bucket_name, is_cname=True)

    # 否则使用 Endpoint
    if endpoint and not endpoint.startswith('http'):
        endpoint = 'https://' + endpoint
    elif endpoint and endpoint.startswith('http://'):
        endpoint = endpoint.replace('http://', 'https://', 1)

    return oss2.Bucket(auth, endpoint, bucket_name)


def get_oss_bucket():
    return create_oss_bucket(
        cfg.get_secret("ACCESS_KEY_ID"),
        cfg.get_secret("ACCESS_KEY_SECRET"),
        cfg.get("ENDPOINT"),
        cfg.get("BUCKET_NAME"),
        cfg.get("OSS_DOMAIN")
    )


def get_local_used_images():
    used_images = set()
    markdown_path = cfg.get("MARKDOWN_PATH")
    if not markdown_path or not os.path.exists(markdown_path):
        return set()
        
    for root, dirs, files in os.walk(markdown_path):
        for file in files:
            if file.endswith('.md'):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = get_oss_url_pattern().findall(content)
                    for m in matches:
                        used_images.add(m)
    return used_images


def get_oss_images():
    bucket = get_oss_bucket()
    oss_files = []
    prefix = cfg.get("PREFIX")
    
    if not prefix:
        raise ValueError("请先配置 PREFIX")

    for obj in oss2.ObjectIterator(bucket, prefix=prefix):
        if obj.key != prefix:
            filename = obj.key.replace(prefix, "")
            if filename:
                # 为每个文件生成一个唯一的预览 URL
                # 前端点击时将调用 /preview?key=xxx 来获取图片
                preview_url = f"/preview?key={urllib.parse.quote(obj.key)}"
                
                oss_files.append({
                    "name": filename,
                    "key": obj.key,
                    "url": preview_url,  # 这里的 URL 用于前端获取图片
                    "size": f"{obj.size / 1024:.2f} KB"
                })
    return oss_files


@app.route('/')
def index():
    try:
        used_set = get_local_used_images()
        all_oss_files = get_oss_images()
        orphans = [f for f in all_oss_files if f['name'] not in used_set]
        return render_template('index.html', orphans=orphans, count=len(orphans))
    except Exception as e:
        # 如果发生错误（如配置缺失），仍然渲染页面，但显示错误信息
        return render_template('index.html', orphans=[], count=0, error=str(e))


@app.route('/delete', methods=['POST'])
def delete_images():
    keys_to_delete = request.json.get('keys', [])
    if not keys_to_delete:
        return jsonify({"status": "error", "message": "未选择文件"})

    try:
        bucket = get_oss_bucket()
        # 阿里云支持批量删除
        result = bucket.batch_delete_objects(keys_to_delete)

        # 属性名从 deleted_objects 改为 deleted_keys
        return jsonify({"status": "success", "deleted": result.deleted_keys})

    except Exception as e:
        # 增加一个异常捕获，防止服务端报错导致前端没反应
        return jsonify({"status": "error", "message": str(e)})


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        data = request.json
        
        # 验证和修复配置数据
        fixed_config, errors = AppConfig.validate_and_fix_config(data)
        
        if errors:
            return jsonify({
                "status": "error",
                "message": "配置验证失败",
                "errors": errors
            }), 400
        
        # 保存修复后的配置
        # Update secrets
        if 'ACCESS_KEY_ID' in fixed_config:
            cfg.set_secret('ACCESS_KEY_ID', fixed_config['ACCESS_KEY_ID'])
        if 'ACCESS_KEY_SECRET' in fixed_config:
            cfg.set_secret('ACCESS_KEY_SECRET', fixed_config['ACCESS_KEY_SECRET'])
        
        # Update standard settings
        for key in ['ENDPOINT', 'BUCKET_NAME', 'OSS_DOMAIN', 'MARKDOWN_PATH', 'PREFIX']:
            if key in fixed_config:
                cfg.set(key, fixed_config[key])
        
        return jsonify({
            "status": "success",
            "message": "配置已保存并修复"
        })
    
    # GET request - return current config
    return jsonify({
        "ACCESS_KEY_ID": cfg.get_secret("ACCESS_KEY_ID") or "",
        "ACCESS_KEY_SECRET": cfg.get_secret("ACCESS_KEY_SECRET") or "",
        "ENDPOINT": cfg.get("ENDPOINT") or "",
        "BUCKET_NAME": cfg.get("BUCKET_NAME") or "",
        "OSS_DOMAIN": cfg.get("OSS_DOMAIN") or "",
        "MARKDOWN_PATH": cfg.get("MARKDOWN_PATH") or "",
        "PREFIX": cfg.get("PREFIX") or ""
    })


@app.route('/test-connection', methods=['POST'])
def test_connection():
    data = request.json
    
    # 验证和修复配置数据
    fixed_config, errors = AppConfig.validate_and_fix_config(data)
    
    if errors:
        return jsonify({
            "status": "error",
            "message": "配置验证失败",
            "errors": errors
        }), 400
    
    try:
        bucket = create_oss_bucket(
            fixed_config.get('ACCESS_KEY_ID'),
            fixed_config.get('ACCESS_KEY_SECRET'),
            fixed_config.get('ENDPOINT'),
            fixed_config.get('BUCKET_NAME'),
            fixed_config.get('OSS_DOMAIN')
        )
        # 尝试获取 Bucket 信息来验证连接和权限
        bucket.get_bucket_info()
        return jsonify({
            "status": "success",
            "message": "连接成功！配置有效。"
        })
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except oss2.exceptions.OssError as e:
        return jsonify({
            "status": "error",
            "message": f"OSS 错误: {e.message} (Code: {e.code})"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"连接失败: {str(e)}"
        }), 400


@app.route('/preview')
def preview_image():
    """获取 OSS 中的图片用于预览
    
    请求参数:
        key: OSS 中的文件 key
    
    返回: 图片的二进制数据
    """
    key = request.args.get('key')
    
    if not key:
        return "Key is required", 400
    
    try:
        bucket = get_oss_bucket()
        # 通过 OSS2 直接获取图片对象
        result = bucket.get_object(key)
        
        # 确定 MIME 类型
        mime_type = result.headers.get('Content-Type')
        if not mime_type or mime_type == 'application/octet-stream':
            mime_type, _ = mimetypes.guess_type(key)
            if not mime_type:
                mime_type = 'application/octet-stream'

        def generate():
            for chunk in result:
                yield chunk
                
        return Response(generate(), mimetype=mime_type)
    except oss2.exceptions.OssError as e:
        return f"OSS Error: {e}", 404
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/select-folder')
def select_folder():
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Open directory selection dialog
        folder_path = filedialog.askdirectory()
        
        # Destroy the root window
        root.destroy()
        
        if folder_path:
            # Normalize path separators
            folder_path = os.path.normpath(folder_path)
            return jsonify({"status": "success", "path": folder_path})
        else:
            return jsonify({"status": "cancelled"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=6900)
