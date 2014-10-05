from cgi import parse_qs, escape
from wsgiref.simple_server import make_server
from server_status import get_info_dict

html_template = """
<html>
    <body>
        <h1> Minecraft Server Status </h1>
        <form method="post" action="parsing_post.wsgi">
            <p>
                Server ip: <input type="text" name="ip">
            </p>
            <p>
                Server port: <input type="text" name="port">
            </p>
            <p>
                <input type="submit" value="Submit">
            </p>
        </form>
        %(results)s
    </body>
</html>
"""

host_template = "<h2> Status for Server: [%(ip)s:%(port)s]: </h2>"

info_template = """
<p>
    %(motd)s - %(version)s <br>
    %(online_players)s/%(max_players)s Players Online:
</p>
"""

players_template = "<ul> %s </ul>"

def application(environ, start_response):
    try:
      request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
      request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body)

    ip   = d.get('ip'  , [''])[0]
    port = d.get('port', [''])[0]

    ip = escape(ip)
    port = escape(port)

    if not port:
        port = 25565

    if ip:

        data = { 'ip' : ip, 'port' : port}
        host = host_template % (data)

        server_info = get_info_dict(ip,int(port))
        info = info_template % (server_info)

        if server_info['players']:
            players = "\n".join(["\t<li>%s</li>" % x for x in server_info['players']])
            players = players_template % players
        else:
            players = "<li>%s</li>" % 'No players online'

        results = host + info + players

    else:
        results = ""

    response_body = html_template % ({'results':results})

    status = '200 OK'

    response_headers = [('Content-Type', 'text/html'),
                  ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)

    return [response_body]

httpd = make_server('localhost', 8051, application)
httpd.serve_forever()
