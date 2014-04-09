Entry data:
    {
        id :: String,
        title :: String
        texts :: [{text_content :: String,
                   text_children :: [String]}]
    }

GET
/get/brief/
    Request Parameters: Page number (default 1)
    Responses: Contains the pagination information of the data returned,
               and for that page the 
    {
        "paging": {
            "current": 1,
            "total": n,
            "count" 10
        },
        "data" : [{
            "id" :: String
            "type" :: String
            "text" :: [String]
            "child_ids" :: [String]
        }]

    }
    Field    type   Description   notes


/get/byname/<id>

POST
/add/

PUT
/change/<id>

DELETE
/delete/all/
/delete/byname/<id>
