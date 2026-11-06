"""Servidor SMTP de prueba (sin TLS, acepta cualquier usuario/clave).
Guarda cada correo recibido organizado por carpetas de fecha YYYY-MM-DD:
 - Formato crudo (.eml) para clientes de correo
 - Formato web (.html) con cabeceras para abrir en el navegador
 - Index diario (index.html) para ver todos los correos del dia en un solo lugar.

Uso:   python Pruebas/smtp_sink.py          (escucha en 127.0.0.1:2525)
Parar: Ctrl+C
"""
import os
import socketserver
import datetime
import email
from email import policy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORREOS_BASE = os.path.join(BASE_DIR, 'correos')
os.makedirs(CORREOS_BASE, exist_ok=True)


def guardar_correo(rcpts, data_bytes):
    hoy = datetime.datetime.now().strftime('%Y-%m-%d')
    dia_dir = os.path.join(CORREOS_BASE, hoy)
    os.makedirs(dia_dir, exist_ok=True)

    # Conteo de correos del dia actual
    existentes = [f for f in os.listdir(dia_dir) if f.endswith('.eml')]
    n = len(existentes) + 1
    prefijo = f'{n:03d}'

    # 1. Guardar EML
    eml_path = os.path.join(dia_dir, f'{prefijo}.eml')
    with open(eml_path, 'wb') as f:
        f.write(('X-Destinatario: ' + ', '.join(rcpts) + '\r\n').encode() + data_bytes)

    # 2. Parsear y Guardar HTML individual
    hora_str = datetime.datetime.now().strftime('%H:%M:%S')
    msg = email.message_from_bytes(data_bytes, policy=policy.default)
    to_hdr = ', '.join(rcpts) if rcpts else str(msg.get('To', ''))
    subj = str(msg.get('Subject', '(Sin asunto)'))
    
    body = msg.get_body(preferencelist=('html', 'plain'))
    html_content = body.get_content() if body else '<p>(Sin contenido)</p>'

    tipo_tag = "Lector"
    if "bibliotecario" in to_hdr.lower() or "resumen" in subj.lower():
        tipo_tag = "Bibliotecario"

    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>{subj}</title>
<style>
  body {{ font-family: Segoe UI, sans-serif; background: #f1f5f9; margin: 0; padding: 24px; }}
  .container {{ max-width: 720px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; }}
  .header {{ background: #0f172a; color: white; padding: 16px 24px; font-size: 13px; line-height: 1.6; }}
  .header b {{ color: #94a3b8; display: inline-block; width: 60px; }}
  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-bottom: 6px; }}
  .tag-lector {{ background: #0284c7; color: white; }}
  .tag-biblio {{ background: #16a34a; color: white; }}
  .content {{ padding: 28px; }}
  .back-btn {{ display: inline-block; margin-bottom: 16px; color: #0284c7; text-decoration: none; font-size: 13px; }}
</style>
</head>
<body>
<div style='max-width:720px;margin:0 auto 12px;'>
  <a class='back-btn' href='index.html'>&larr; Volver a la bandeja del día ({hoy})</a>
</div>
<div class='container'>
  <div class='header'>
    <span class='tag {"tag-biblio" if tipo_tag == "Bibliotecario" else "tag-lector"}'>{tipo_tag}</span>
    <div><b>De:</b> Biblioteca ReadOut &lt;biblioteca.readout@test.local&gt;</div>
    <div><b>Para:</b> {to_hdr}</div>
    <div><b>Fecha:</b> {hoy} {hora_str}</div>
    <div><b>Asunto:</b> {subj}</div>
  </div>
  <div class='content'>
    {html_content}
  </div>
</div>
</body>
</html>"""

    html_path = os.path.join(dia_dir, f'{prefijo}.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_wrapper)

    # 3. Actualizar index.html del día
    actualizar_index_dia(dia_dir, hoy)

    print(f'[{hoy} {hora_str}] Correo #{prefijo} [{tipo_tag}] -> {to_hdr} | Asunto: {subj}', flush=True)


def actualizar_index_dia(dia_dir, hoy):
    archivos_html = sorted([f for f in os.listdir(dia_dir) if f.endswith('.html') and f != 'index.html'])
    
    filas = []
    for h in archivos_html:
        eml_name = h.replace('.html', '.eml')
        eml_path = os.path.join(dia_dir, eml_name)
        to_hdr = ''
        subj = ''
        if os.path.exists(eml_path):
            with open(eml_path, 'rb') as fp:
                m = email.message_from_binary_file(fp, policy=policy.default)
                to_hdr = str(m.get('To', m.get('X-Destinatario', '')))
                subj = str(m.get('Subject', ''))
        
        tipo = "Bibliotecario" if "bibliotecario" in to_hdr.lower() or "resumen" in subj.lower() else "Lector"
        badge_style = "background:#dcfce7;color:#166534;" if tipo == "Bibliotecario" else "background:#e0f2fe;color:#0369a1;"
        
        filas.append(f"""
        <tr>
          <td style='padding:10px 14px;border-bottom:1px solid #e2e8f0;font-weight:600;'>#{h[:3]}</td>
          <td style='padding:10px 14px;border-bottom:1px solid #e2e8f0;'>
            <span style='padding:3px 8px;border-radius:12px;font-size:11px;font-weight:bold;{badge_style}'>{tipo}</span>
          </td>
          <td style='padding:10px 14px;border-bottom:1px solid #e2e8f0;'>{to_hdr}</td>
          <td style='padding:10px 14px;border-bottom:1px solid #e2e8f0;'>
            <a href='{h}' style='color:#2563eb;text-decoration:none;font-weight:500;'>{subj}</a>
          </td>
          <td style='padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;'>
            <a href='{h}' style='padding:4px 10px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:4px;color:#334155;text-decoration:none;font-size:12px;margin-right:6px;'>Ver Web</a>
            <a href='{eml_name}' style='padding:4px 10px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:4px;color:#334155;text-decoration:none;font-size:12px;'>Descargar .eml</a>
          </td>
        </tr>
        """)

    index_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Bandeja de Pruebas RPA - {hoy}</title>
<style>
  body {{ font-family: Segoe UI, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 32px; }}
  .container {{ max-width: 980px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); padding: 28px; }}
  h1 {{ margin-top: 0; font-size: 22px; color: #0f172a; }}
  p {{ color: #64748b; font-size: 14px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
  th {{ background: #f1f5f9; padding: 12px 14px; text-align: left; font-size: 12px; color: #475569; text-transform: uppercase; border-bottom: 2px solid #cbd5e1; }}
</style>
</head>
<body>
<div class='container'>
  <h1>📬 Bandeja de Correos Interceptados (Día: {hoy})</h1>
  <p>Total de correos generados hoy por el Bot de UiPath: <b>{len(archivos_html)}</b></p>
  <table>
    <thead>
      <tr>
        <th style='width:50px;'>#</th>
        <th style='width:110px;'>Destino</th>
        <th style='width:220px;'>Para</th>
        <th>Asunto</th>
        <th style='width:180px;text-align:right;'>Acción</th>
      </tr>
    </thead>
    <tbody>
      {''.join(filas)}
    </tbody>
  </table>
</div>
</body>
</html>"""

    with open(os.path.join(dia_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)


class Smtp(socketserver.StreamRequestHandler):
    def handle(self):
        w = lambda s: self.wfile.write((s + '\r\n').encode())
        w('220 sink ESMTP')
        rcpts = []
        while True:
            line = self.rfile.readline()
            if not line:
                return
            c = line.decode('latin1').strip()
            up = c.upper()
            if up.startswith('EHLO'):
                self.wfile.write(b'250-sink\r\n250-AUTH PLAIN LOGIN\r\n250 8BITMIME\r\n')
            elif up.startswith('AUTH PLAIN'):
                w('235 ok')
            elif up.startswith('AUTH LOGIN'):
                if len(c.split()) > 2:
                    w('334 UGFzc3dvcmQ6'); self.rfile.readline(); w('235 ok')
                else:
                    w('334 VXNlcm5hbWU6'); self.rfile.readline(); w('334 UGFzc3dvcmQ6'); self.rfile.readline(); w('235 ok')
            elif up.startswith('RCPT TO'):
                rcpts.append(c[8:].strip(' <>')); w('250 ok')
            elif up == 'DATA':
                w('354 go')
                buf = b''
                while True:
                    l = self.rfile.readline()
                    if l in (b'.\r\n', b''):
                        break
                    buf += l
                guardar_correo(rcpts, buf)
                w('250 queued'); rcpts = []
            elif up == 'QUIT':
                w('221 bye'); return
            else:
                w('250 ok')


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    print('SMTP de prueba activo en 127.0.0.1:2525', flush=True)
    print('Organizando correos por carpetas diarias en:', CORREOS_BASE, flush=True)
    Server(('127.0.0.1', 2525), Smtp).serve_forever()
