from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from db.restaurants_repository import RestaurantRepository
import traceback
import cgi

HTML_START = "<html><body>"
HTML_END = "<html><body>"

repository = RestaurantRepository()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                allRestaurants = repository.readAll()

                message = HTML_START
                message += "<a href='/restaurants/new'>Make a new restaurant</a> </br></br>"
                for restaurant in allRestaurants:
                    message += restaurant.name + "</br>"
                    message += "<a href='/restaurant/%s/edit'>Edit</a> </br>" % restaurant.id
                    message += "<a href='/restaurant/%s/delete'>Delete</a> </br>" % restaurant.id
                    message += "</br>"
                message += HTML_END

                self.wfile.write(message)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                message = HTML_START
                message += "<h1>Create a new restaurant</h1> </br></br>"
                message += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Name</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                message += HTML_END

                self.wfile.write(message)
                return

            if self.path.endswith("/edit"):
                restaurantIdPath = self.path.split("/")[2]
                restaurant = repository.readById(restaurantIdPath)

                if (restaurant != []):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
    
                    message = HTML_START
                    message += "<h1>%s</h1> </br>" % restaurant.name
                    message += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><h2>New name</h2><input name="message" type="text"><input type="submit" value="Submit"> </form>''' % restaurantIdPath
                    message += HTML_END

                    self.wfile.write(message)
                return

            if self.path.endswith("/delete"):
                restaurantIdPath = self.path.split("/")[2]
                restaurant = repository.readById(restaurantIdPath)

                if (restaurant != []):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    message = HTML_START
                    message += "<h1>Are you sure you want to delete restaurant %s?</h1> </br>" % restaurant.name
                    message += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'> <input type="submit" value="Delete"> </form>''' % restaurantIdPath
                    message += "<form action='/restaurants'> <input type='submit' value='Cancel'/> </form>"
                    message += HTML_END

                    self.wfile.write(message)
                return

        except:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newName = fields.get('message')
                    repository.create(newName[0])
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantIdPath = self.path.split("/")[2]
                    newName = fields.get('message')
                    repository.update(restaurantIdPath, newName[0])

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    restaurantIdPath = self.path.split("/")[2]
                    repository.delete(restaurantIdPath)

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return

        except:
            print("something went wrong")
            traceback.print_exc()


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()


if __name__ == '__main__':
    main()
