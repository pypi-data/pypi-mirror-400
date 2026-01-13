from gllm_core.schema import Chunk
from gllm_datastore.constants import SIMILARITY_SCORE as SIMILARITY_SCORE
from langchain_core.documents import Document

def from_langchain(doc: Document, score: float | None = None) -> Chunk:
    """Create a standardized Chunk from a LangChain Document.

    Args:
        doc (Document): The document to create a Chunk from.
        score (float | None, optional): The score to assign to the Chunk. Defaults to None, in which case it will
            attempt to get the score from the `score` metadata.

    Returns:
        Chunk: The standardized Chunk object.
    """
def to_langchain(chunk: Chunk) -> Document:
    """Create a LangChain Document from a standardized Chunk.

    Args:
        chunk (Chunk): The standardized Chunk to create a Document from.

    Returns:
        Document: The LangChain Document object.
    """
def l2_distance_to_similarity_score(distance: float) -> float:
    """Convert distance to similarity.

    Args:
        distance (float): The distance value to convert. Ranges in [0, inf].

    Returns:
        float: The converted similarity value.
    """
def cosine_distance_to_similarity_score(distance: float) -> float:
    """Convert cosine distance to similarity.

    Args:
        distance (float): The cosine distance value to convert. Ranges in [0, 2].

    Returns:
        float: The converted similarity value. Ranges in [0, 1].
    """
def similarity_score_to_cosine_distance(similarity: float) -> float:
    """Convert similarity to cosine distance.

    Args:
        similarity (float): The similarity value to convert. Ranges in [0, 1].

    Returns:
        float: The converted cosine distance value. Ranges in [0, 2].
    """
