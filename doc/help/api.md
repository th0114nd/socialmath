This is the socialmath api v0.1. Fields are subject to$
change with little notice.


**HTTP GET**

`/get/brief`

`/get/brief?page=n`

*Request Parameters:* Page number (default 1)

*Responses:* Contains the pagination information of the data returned,
           and for that page a list of short form structure of the
           tree. For `child_ids` of a theorem T or definitions, they
           may be either the union of the children for all proofs
           of T or the children for any particular proof, e.g.
           the first: this is purely for the high level view.
           `200` on success. If the page number is too high,
           response could either be a `404` or a `200` with a$
           count of 0 in the paging.
*Typing:*
   $
    {
        paging :: {
            current :: Int
            total :: Int
            count :: Int
        }
        data :: [{
            id :: Int
            kind :: Axiom | Theorem | Definition
            child_ids :: [Int]
        }]
    }
  $
*Example:*

    $ curl -X GET api.socialmath.com/get/brief
    {"paging":{"current":1,"total":1,"count":2}
     "data":[{"id":1, "kind":"axiom", "child_ids":[]},
             {"id":2, "kind":"theorem", "child_ids":[1]}]}

`/get/medium`

`/get/medium?page=n`

*Request Parameters:* Page number (default 1)

*Responses:* Like the brief request, but also includes the statement
    of each theorem/definition/axiom, and doesn't have the body. The
    hope is that it is easy enough to implement both with similar
    code server side and save an bandwith in the HTTP requests if
    need be.

*Typing:*

    {
        paging :: {
            current :: Int
            total :: Int
            count :: Int
        }
        data :: [{
            id :: Int
            kind :: Axiom | Theorem | Definition
            statement :: String
            child_ids :: [Int]
        }]
    }

*Example:*

    $ curl -X GET api.socialmath.com/get/medium
    {"paging":{"current":1,"total":1,"count":2}
     "data":[{"id":1, "kind":"axiom", "statement": "There exists an additive inverse", "child_ids":[]},
             {"id":2, "kind":"theorem", "statement" "There is a unique additive inverse", "child_ids:[1]}]}

`/get/one/`

*Responses:* `400` Bad Request. An id is required.

`/get/one/<id>`

*Request Parameters:* None

*Responses:*$

`200` means the payload is the database entry associated with
that id as well as its immediate neighbors.

`404` means that id was never in the database

`410` means that the id has since been deleted.

*Typing:*
Construct is the type of an individual node, more or less how
it is stored server side.

    type Construct = {
        id :: Int
        kind :: Axiom | Theorem | Definition
        date :: Timestamp
        title :: String
        bodies :: [{proof_id :: Int$
                    content :: String
                    below_neighbors :: [Int]]
        above_neighbors :: [Int]
    }
The response itself is like

    {
        wanted :: Construct // The requested for DAG entry.
        neighbors :: [Construct] // Above and below neighbors in full.
    }

*Example:*

    $ curl -X GET api.socialmath.com/get/one/2
    {"wanted":{"id":2, "kind":"theorem", "date":"4/17/14",$
                "title":"There is a unique additive inverse",
                "bodies":[{"proof_id":1,$
                           "content":"Assume there are two additive inverses...",$
                           "below_neighbors": [1]},
                          {"proof_id":2,
                           "content": "Z is a ring, therefore...",$
                           "below_neighbors": [1]}]
                "above_neighbors": []},
     "neighbors":[{"id":1, "kind":"axiom", "date":"4/16/14",
                "title": "There exists an additive inverse",
                "bodies":[],
                "above_neighbors":[2]}]}


**HTTP POST**

`/add/`

*Request Parameters:* None

*Request body:*

    {
        kind :: String
        title :: String
        body :: String
        below_neighbors :: [Int]
    }

*Responses:*

`200` means the resource was successfully created

`500` means there was a problem with creation

*Typing:*

    // id and date published assigned by the server
    {
        id :: Int
        date :: Timestamp
    }

*Example:*

    $ curl -X POST -d '{"kind":"theorem", "title": "$\forall a \in Z, a \cdot 0 = 0", \
    > "body": "$a \cdot 0 = a \cdot (0 + 0) = ...", "below_neighbors"=[2]} \
    > api.socialmath.com/add/
    {"id":3, "date":"4/18/14"}

    $ curl -X GET api.socialmath.com/get/one/3
    {"wanted":{"id": 3, "kind":"theorem", "date":"4/18/14",
                "title": "$\forall a \in Z, a \cdot 0 = 0$",
                "bodies": [{"proof_id": 1,
                           "content": "$a \cdot 0 = a \cdot (0 + 0) = ...",
                           "below_neighbors": [2]}]
                "above_neighbors"=[]},
     "neighbors":[{"id":2,... }]}

`/add/proof/<id>`
 Adds a proofbody or an alternative explanation to a construct

*Request Parameters*: None

*Request Body*:

    {
        body :: String
        below_neighbors :: [Int]
    }

*Responses:*

`200` means the body was successfully inserted.

`404` means that the id has never existed.

`410` means that the id has been deleted.$

*Example:*

    $ curl -I -X POST -d '{"body": "Assume not. Then...", "below_neighbors":[2]} \
    > api.socialmath.com/add/proof/3 | grep "HTTP"
    HTTP/1.1 200 OK

**HTTP PUT**

`/change/<id>/`

Changes something about the construct identified by id.

*Request Parameters:* None.

*Request Body:*
Note that if you leave the kind or title as null, it is not updated.

    {
        title :: Null | String
        kind :: Null | String
    }

*Responses:*

`200` means the change was successful.

`404` means the id never existed.

`410` means the id has since been deleted.

*Typing:*

    {
        id :: Int
        newdate :: Timestamp
    }

*Example:*

    $ curl -X PUT -d '{"title": "Additive inverses exist", "kind":null}' \
    > api.socialmath.com/change/1
    {"id": 1, "newdate":"4/20/14"}
    $ curl -X GET api.socialmath.com/get/one/1
    {"wanted":{"id":1, "kind":"axiom", "date":"4/20/14",$
                "title":"Additive inverses exist",
                "bodies":[],
                "above_neighbors": [2],
                "below_neigbors": [1]},
     "neighbors":[...]}

`/changeproof/<id>/<proofid>`
Alters a particular proof for a theorem.

*Request Parameters:* None

*Request Body:*

    {
        body :: Null | String
        below_neighbors :: Null | [Int]
    }

*Responses:*

`200` change was successful

`404` means the theorem id never existed or it has no proof with that id

`410` means the theorem id has been deleted or the proof with that id has been deleted.

*Typing:*

    {
        id :: Int
        proof_id :: Int
        newdate :: Timestamp
    }

*Example:*
   $
    $ curl -X PUT -d '{"body":null, "below_neighbors":[1, 2]}' api.socialmath.com/change/3/1
    {"id":3, "proof_id":1, "newdate":"4/20/14"}
   $

`/delete/all/`

`/delete/one/<id>`

`/delete/proof/<id>/<proofid>`

Removes either the entire tree or a particular construct or a proof for that construct.
If a particular construct, removes that

*Request Parameters:* None.

*Responses:*

`200` on successful deletion

`403` if we implement accounts and they do not have$
    sufficient authorization

`404` if the id was never part of the dag.

`410` if the id would have been found, but was already deleted.

*Example:*

    $ curl -I -X GET api.socialmath.com/get/one/9000 | grep HTTP
    HTTP/1.1 404 Not Found
    $ curl -I -X PUT -d '{}' api.socialmath.com/delete/one/9000 | grep HTTP
    HTTP/1.1 404 Not Found
    $ curl -I -X GET api.socialmath.com/get/one/2 | grep HTTP
    HTTP/1.1 200 OK
    $ curl -I -X PUT -d '{}' api.socialmath.com/delete/one/2 | grep HTTP
    HTTP/1.1 200 OK
    $ curl -I -X GET api.socialmath.com/get/one/2 |grep HTTP
    HTTP/1.1 410 Gone
    $ curl -I -X GET api.socialmath.com/delete/one/2 | grep HTTP
    HTTP/1.1 410 Gone
    $ curl -I -X PUT -d '{}' api.socailmath.com/delete/all/ | grep HTTP
    HTTP/1.1 200 OK
    $ curl -X GET api.socialmath.com/get/brief
    {"paging":{"current":1, "total":1, "count":0}, "data":[]}
