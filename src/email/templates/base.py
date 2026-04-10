def base_template(content: str, preheader: str = "") -> str:
    """Template HTML de base pour tous les emails Emerging-Stream."""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Emerging-Stream</title>
<style>
  body {{ margin:0; padding:0; background:#080a0f; font-family:'Segoe UI',Arial,sans-serif; color:#f0ede8; }}
  .wrapper {{ max-width:600px; margin:0 auto; padding:20px; }}
  .header {{ background:linear-gradient(135deg,#1a1508,#0d1117); border-radius:16px 16px 0 0; padding:32px; text-align:center; border-bottom:2px solid #c9a84c; }}
  .logo {{ font-size:28px; font-weight:700; color:#f0ede8; letter-spacing:-0.5px; }}
  .logo span {{ color:#c9a84c; }}
  .body {{ background:#12181f; padding:40px 32px; border-radius:0 0 16px 16px; border:1px solid rgba(255,255,255,0.07); border-top:none; }}
  .btn {{ display:inline-block; background:linear-gradient(135deg,#c9a84c,#e8c96a); color:#0a0800!important; font-weight:700; padding:14px 32px; border-radius:100px; text-decoration:none; font-size:16px; margin:20px 0; }}
  .code-box {{ background:#0d1117; border:2px dashed #c9a84c; border-radius:12px; padding:20px; text-align:center; margin:24px 0; }}
  .code {{ font-family:monospace; font-size:24px; font-weight:700; color:#c9a84c; letter-spacing:4px; }}
  .divider {{ border:none; border-top:1px solid rgba(255,255,255,0.07); margin:24px 0; }}
  .footer {{ text-align:center; padding:24px; color:#7a8694; font-size:13px; }}
  .highlight {{ color:#c9a84c; font-weight:600; }}
  .tag {{ background:rgba(201,168,76,0.1); border:1px solid rgba(201,168,76,0.3); border-radius:100px; padding:4px 14px; font-size:12px; color:#c9a84c; display:inline-block; margin-bottom:16px; }}
  h1 {{ font-size:26px; font-weight:700; margin:0 0 8px; line-height:1.3; }}
  p {{ color:#c8c4be; line-height:1.8; margin:0 0 16px; }}
  ul {{ color:#c8c4be; line-height:2; padding-left:20px; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="logo">Emerging<span>Stream</span> 🎬</div>
  </div>
  <div class="body">
    {content}
  </div>
  <div class="footer">
    © 2025 Emerging-Stream · Tous droits réservés<br/>
    <a href="mailto:support@emerging-stream.com" style="color:#c9a84c;">support@emerging-stream.com</a>
  </div>
</div>
</body>
</html>
"""
