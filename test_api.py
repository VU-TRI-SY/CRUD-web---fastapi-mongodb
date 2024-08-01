from requests import get, post, put, delete, HTTPError

def test_api():
    book_root = "http://localhost:8000/books/"

    initial_doc = {"title" : "Collective Intelligence in Action", "isbn" : "001", "categories" : [ "Internet" ]}

    docs = [
        {"title" : "Unlocking Android", "isbn" : "002", "categories" : [ "Open Source", "Mobile" ] },
	    {"title" : "Android in Action, Second Edition", "isbn" : "003", "categories" : [ "Java" ] },
        {"title" : "Specification by Example", "isbn" : "004", "categories" : [ "Software Engineering" ] },
        {"title" : "Flex 3 in Action", "isbn" : "005", "categories" : [ "Internet" ] }
    ]

    try:
        # test post
        response = post(book_root, json=initial_doc)
        response.raise_for_status()
        doc = response.json()
        inserted_id = doc["_id"]
        print(f"Inserted document with id: {inserted_id}")
        print(
            "If the test fails in the middle you may want to manually remove the document."
        )
        assert doc["title"] == "Collective Intelligence in Action"
        assert doc["isbn"] == "001"
        assert "Internet" in doc["categories"]

        # get all items
        for doc in docs:
            post(book_root, json=doc)
        
        response = get(book_root)
        response.raise_for_status()
        student_ids = {s["_id"] for s in response.json()}
        assert inserted_id in student_ids

        # get individual item
        response = get(f'{book_root}?id={inserted_id}')
        response.raise_for_status()
        doc = response.json()[-1]
        assert doc["title"] == "Collective Intelligence in Action"
        assert doc["isbn"] == "001"
        assert "Internet" in doc["categories"]

        # Update the item
        response = put(
            book_root + inserted_id,
            json={
                "categories" : [ "Internet", "Web", "Machine Leanring", "Deep Learning"]
            },
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["_id"] == inserted_id
        assert doc["title"] == "Collective Intelligence in Action"
        assert doc["isbn"] == "001"
        assert "Web" in doc["categories"]
        assert "Machine Leanring" in doc["categories"]

        # Get the item and check for change
        response = get(f'{book_root}?id={inserted_id}')
        response.raise_for_status()
        doc = response.json()[-1]
        assert doc["_id"] == inserted_id
        assert doc["title"] == "Collective Intelligence in Action"
        assert doc["isbn"] == "001"
        assert "Web" in doc["categories"]
        assert "Machine Leanring" in doc["categories"]

        # Delete the doc
        response = delete(book_root + inserted_id)
        response.raise_for_status()
        assert response.status_code == 204
        # Get the doc and ensure it's been deleted
        response = get(f'{book_root}?id={inserted_id}')
        assert len(response.json()) == 0
    except HTTPError as he:
        print(he.response.json())
        raise