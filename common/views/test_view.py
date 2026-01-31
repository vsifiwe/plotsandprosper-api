# common/views/test_view.py

from rest_framework.response import Response

def test_view(request):
    """
    Test view
    """
    return Response({"message": "Hello, World!"})
