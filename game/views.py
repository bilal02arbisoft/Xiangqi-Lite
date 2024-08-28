from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from game.models import Game
from game.serializers import GameSerializer


class GameCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        game_data = {
            "red_player": None,
            "black_player": None,
            "fen": "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r",
            "initial_fen": "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r",
            "moves": "[]",
            "turn": "red",
            "status": "ongoing"
        }

        serializer = GameSerializer(data=game_data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameUpdateView(APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:

            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, game_id=game_id)
        serializer = GameSerializer(game)

        return Response(serializer.data, status=status.HTTP_200_OK)

