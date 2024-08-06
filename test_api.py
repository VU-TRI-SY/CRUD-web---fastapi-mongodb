from requests import get, post, put, delete, HTTPError

def test_api():
    book_root = "http://localhost:8000/book/"

    initial_doc = {
        "id" : 10,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "published_date": "1813-01-28",
        "isbn": "8781503290563",
        "pages": 279,
        "cover": "https://example.com/pride-and-prejudice.jpg",
        "language": "English",
        "price": 6.99
    }


    try:
        # test post
        response = post(book_root, json=initial_doc)
        response.raise_for_status()
        doc = response.json()
        inserted_id = doc["id"]
        print(f"Inserted document with id: {inserted_id}")
        print(
            "If the test fails in the middle you may want to manually remove the document."
        )

        assert doc["title"] == "Pride and Prejudice"
        assert doc["author"] == "Jane Austen"
        assert doc["isbn"] == "8781503290563"

        # # get all items
        # for doc in docs:
        #     post(book_root, json=doc)
        
        response = get(book_root)
        response.raise_for_status()
        student_ids = {s["id"] for s in response.json()}
        assert inserted_id in student_ids

        # get individual item
        response = get(f'{book_root}?id={inserted_id}')
        response.raise_for_status()
        doc = response.json()
        assert doc["title"] == "Pride and Prejudice"
        assert doc["author"] == "Jane Austen"
        assert doc["isbn"] == "8781503290563"

        # # Update the item
        response = put(
            book_root + str(inserted_id),
            json={
                "title" : "Pride and Prejudice - updated"
            },
        )

        response.raise_for_status()
        doc = response.json()
        assert doc["id"] == inserted_id
        assert doc["title"] == "Pride and Prejudice - updated"
        assert doc["author"] == "Jane Austen"
        assert doc["isbn"] == "8781503290563"

        # Get the item and check for change
        response = get(f'{book_root}?id={inserted_id}')
        response.raise_for_status()
        doc = response.json()
        assert doc["id"] == inserted_id
        assert doc["title"] == "Pride and Prejudice - updated"

        # Delete the doc
        response = delete(book_root + str(inserted_id))
        response.raise_for_status()
        assert response.status_code == 204
        # Get the doc and ensure it's been deleted
        response = get(f'{book_root}?id={inserted_id}')
        assert response.json() == None
    except HTTPError as he:
        print(he.response.json())
        raise