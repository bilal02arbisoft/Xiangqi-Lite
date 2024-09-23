from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from game.models import Game
from game.serializers import GameSerializer
from game.utils import hashids


class BaseAPIView(APIView):
    """
    Base API view that includes default permission classes and error handling.
    All views inheriting from this class will automatically apply the error handling decorator.
    """
    permission_classes = [IsAuthenticated]

class GameCreateView(BaseAPIView):
    """
    Handles the creation of a new game instance.
    This view receives a POST request to initialize a game with default values,
    including players, board configuration (FEN), and game status. It validates
    the input using the GameSerializer and saves the game if valid.
    """
    def post(self, request, *args, **kwargs):
        game_data = {
            'red_player': None,
            'black_player': None,
            'fen': 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r',
            'initial_fen': 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r',
            'moves': [],
            'turn': 'red',
            'status': 'ongoing',
            'viewers': None
        }
        serializer = GameSerializer(data=game_data)
        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GameDetailView(BaseAPIView):
    """
    Retrieves the details of a specific game.
    This view handles GET requests for fetching the details of a game by its ID.
    The game ID is decoded, and the game is retrieved from the database. If the
    game is found, it returns the game data, otherwise an error is returned.
    """
    def get(self, request, game_id, *args, **kwargs):
        decoded_id = hashids.decode(game_id)
        if not decoded_id:

            return Response({'error': 'Invalid game ID'}, status=status.HTTP_404_NOT_FOUND)

        game = get_object_or_404(Game, id=decoded_id[0])
        serializer = GameSerializer(game)

        return Response(serializer.data, status=status.HTTP_200_OK)

class GameUpdateView(BaseAPIView):
    """
    Updates an existing game instance.
    This view handles PUT requests to update a game by its ID. The game data is
    partially updated based on the provided input. The game ID is decoded, and
    if valid, the corresponding game is updated.
    """
    def put(self, request, game_id, *args, **kwargs):
        decoded_id = hashids.decode(game_id)
        if not decoded_id:

            return Response({'error': 'Invalid game ID'}, status=status.HTTP_404_NOT_FOUND)
        game = get_object_or_404(Game, id=decoded_id[0])
        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
