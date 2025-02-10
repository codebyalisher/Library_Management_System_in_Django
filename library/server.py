import requests

headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MTM0MjE4LCJpYXQiOjE3MzkwOTEwMTgsImp0aSI6IjAyNjAyZWU2MzBmYTQxNzRiZjdlNGQ1NDdjYjMxZDI5IiwidXNlcl9pZCI6MX0.TV0wAm4XTLX_eQj2Hme3AqfOnHIjSFsZ5inI80AKhu0'
}

response = requests.delete('http://127.0.0.1:8000/api/crud/authors/1/', headers=headers)
print(response.json())  # Check the response
