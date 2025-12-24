from comments.serializers import CommentSerializer
from galfies.serializers import GalfySerializer
from reviews.serializers import ReviewSerializer
from reviews.models import Review
from comments.models import Comment
from galfies.models import Galfy

def find_serializer_feed_item(obj, request):
    if isinstance(obj, Galfy):
        return GalfySerializer(obj, context={"request": request})
    elif isinstance(obj, Comment):
        return CommentSerializer(obj, context={"request": request})
    elif isinstance(obj, Review):
        return ReviewSerializer(obj, context={"request": request})
    else:
        raise TypeError
