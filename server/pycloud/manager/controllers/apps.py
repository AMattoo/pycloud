import logging
import json
import urllib

from bson import ObjectId

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML
from webhelpers.html import literal

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.manager.lib.pages import AppsPage
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.model import App, Service


log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class AppsController(BaseController):

    JSON_OK = {"STATUS" : "OK" }
    JSON_NOT_OK = { "STATUS" : "NOT OK"}

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_list()

    ############################################################################################################
    # Shows the list of stored Apps.
    ############################################################################################################
    def GET_list(self):
        # Mark the active tab.
        c.apps_active = 'active'    
        
        # Create the actual page.
        page = AppsPage()
        
        # Setup the page to render.
        page.form_values = {}
        page.form_errors = {}
    
        # Get a list of existing stored apps.
        apps = App.find()

        # Create an item list with the info to display.
        grid_items = []
        for app in apps:
            new_item = {'name': app.name,
                       'service_id': app.service_id,
                       'description': app.description,
                       'version': app.app_version,
                       'min_android_version': app.min_android_version,
                       'actions': 'Edit',
                       'id': app._id}
            grid_items.append(new_item)

        # Create and fomat the grid.
        appsGrid = Grid(grid_items, ['name', 'service_id', 'description', 'version', 'min_android_version', 'actions'])
        appsGrid.column_formats["actions"] = generateActionButtons
        
        # Prepare service list.
        page.stored_services = {}
        services = Service.find()
        for service in services:
            page.stored_services[service._id] = service._id;          
        
        # Pass the grid and render the page.
        page.appsGrid = appsGrid
        return page.render()

    ############################################################################################################
    # Gets data for an app.
    ############################################################################################################
    @asjson    
    def POST_get_data(self):
        # Parse the body of the request as JSON into a python object.
        # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
        parsedJsonString = urllib.unquote(request.body)[:-1]
        fields = json.loads(parsedJsonString)
        print 'App data request received, data: ' + parsedJsonString
                
        # Get a list of existing stored apps.
        app_id = ObjectId(fields['appId'])
        app = App.by_id(app_id)
        
        if not app:
            # If there was a problem getting the app to update, return a json-formated error.
            print 'Error getting app data: app was not found'
            return self.JSON_NOT_OK        

        return app

    ############################################################################################################
    # Load
    ############################################################################################################
    @asjson
    def POST_edit(self):
        # Parse the body of the request as JSON into a python object.
        # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
        parsedJsonString = urllib.unquote(request.body)[:-1]
        fields = json.loads(parsedJsonString)
        print 'App creation request received, data: ' + parsedJsonString    
        
        try:
            # Create a new app object if we are adding, or get the current if we are updating.
            if fields['appId'] == '':
                app = App()
            else:
                # Get the existing app from the DB, if it can be found.
                app = App.by_id(ObjectId(fields['appId']))                
                if not app:
                    # If there was a problem getting the app to update, return a json-formated error.
                    print 'Error getting app to modify: app was not found'
                    return self.JSON_NOT_OK
            
            # Set the values for all the apps' fields.
            app.name = fields['name']
            app.service_id = fields['serviceId']
            app.description = fields['description']
            app.app_version = fields['version']
            app.package_name = fields['package']
            app.tags = fields['tags']
            app.min_android_version = fields['minOsVersion']
            
            # TODO add these to the DB. APK will be different, md5 will have to be calculated.
            app.apk_file = None
            app.md5sum = None
            
            # Save the new/updated app to the DB.
            app.save()
            print 'App data stored.'
        except Exception as e:
            # If there was a problem creating the app, return a json-formated error.
            print 'Error creating App: ' + str(e)
            return self.JSON_NOT_OK
        
        # Everything went well.
        print 'Returning success'
        return self.JSON_OK    
        
    ############################################################################################################
    # Removes a stored app.
    ############################################################################################################
    @asjson       
    def POST_remove(self):
        # Parse the body of the request as JSON into a python object.
        # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
        parsedJsonString = urllib.unquote(request.body)[:-1]
        fields = json.loads(parsedJsonString)
        print 'App removal request received, data: ' + parsedJsonString        
        
        try:
            # Remove the app.
            appId = ObjectId(fields['appId'])
            app = App.find_and_remove(appId)
            
            # Check if we succeeded.
            if app:
                print 'App removed.'
            else:
                print 'Error removing app: app was not found.'
                return self.JSON_NOT_OK                
        except Exception as e:
            print 'Error removing App: ' + str(e)
            return self.JSON_NOT_OK
        
        # Everything went well.
        return self.JSON_OK        

############################################################################################################
# Helper function to generate buttons to edit or delete apps.
############################################################################################################        
def generateActionButtons(col_num, i, item):
    # Link and button to edit the app.
    getAppDataURL = h.url_for(controller='apps', action='get_data')
    editButton = HTML.button("Edit App", onclick=literal("loadAppData('" + getAppDataURL + "', '" + str(item["id"]) + "')"), class_="btn btn-primary")

    # Ajax URL to remove the app.
    removeAppURL = h.url_for(controller='apps', action='remove')
    removeButton = HTML.button("Remove App", onclick="removeAppConfirmation('" + removeAppURL + "', '" + str(item["id"])  + "', '" + str(item["name"]) + "');", class_="btn btn-primary btn")
    
    # Render the buttons.
    return HTML.td(editButton + literal("&nbsp;") + removeButton  )       
