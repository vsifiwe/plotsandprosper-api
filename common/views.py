# common/views.py

from rest_framework.response import Response

def test_view(request):
    """
    Test view
    """
    return Response({"message": "Hello, World!"})
