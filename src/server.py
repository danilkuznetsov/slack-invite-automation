import BaseHTTPServer
import cgi
import urlparse
import requests
import json
import sys


HOST_NAME = 'localhost' 
PORT_NUMBER = 1710


class SlackInviteHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            post_vars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            post_vars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            post_vars = {}

        result = self.get_invite(post_vars)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(result)

    def get_invite(self, post_vars):

        sys.stderr.write("user request {msg} \n".format(msg=post_vars))

	token = '<slack token>'
        url = 'https://<slack_team_name>.slack.com/api/users.admin.invite'
	            
        payload = {"email": post_vars['email'], "set_active": "true",
                   "token": token}
        response = []
        try:
            response = requests.post(url, data=payload)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            return json.dumps({
                "correct": False,
                "msg": "Failed request on slack"
            })

        sys.stderr.write("slack response {msg} \n".format(msg=response.text))

        r = json.loads(response.text)

        if r['ok']:
            return json.dumps({
                "correct": True,
                "msg": "Success! Check {msg} for an invite from Slack.".format(msg=post_vars['email'])
            })
        elif r['error'] == 'already_invited':
            return json.dumps({
                "correct": True,
                "msg": "Success! You were already invited.<br> Visit to <a href='{url}'> slack community </a>".format(
                        url="https://<slack_team_name>.slack.com/")
            })

        elif r['error'] == 'already_in_team':
            return json.dumps({
                "correct": True,
                "msg": "Success! You were already invited.<br> Visit to <a href='{url}'> slack community</a>".format(
                        url="https://<slack_team_name>.slack.com/")
            })

        elif r['error'] == 'invalid_email':
            return json.dumps({
                "correct": False,
                "msg": "The email you entered is an invalid email."
            })
        elif r['error'] == 'invalid_auth':
            return json.dumps({
                "correct": False,
                "msg": "Something has gone wrong. Please contact a system administrator."
            })
        else:
            return json.dumps({
                "correct": False,
                "msg": "Something has gone wrong. Please contact a system administrator."
            })


if __name__ == "__main__":
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), SlackInviteHandler)
    sys.stderr.write("Server Start - %s:%s \n" % (HOST_NAME, PORT_NUMBER))
    try:
   	 httpd.serve_forever()
    except KeyboardInterrupt:
  	  pass
    httpd.server_close()
    sys.stderr.write( "Server Stop - %s:%s \n" % (HOST_NAME, PORT_NUMBER))
