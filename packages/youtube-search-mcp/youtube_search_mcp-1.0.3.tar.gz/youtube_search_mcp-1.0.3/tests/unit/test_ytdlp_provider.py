
import pytest
from unittest.mock import MagicMock, patch
from youtube_search_mcp.search.ytdlp_provider import YtDlpSearchProvider
from youtube_search_mcp.core.exceptions import SearchProviderError

@pytest.fixture
def provider():
    return YtDlpSearchProvider()

def test_execute_playlist_search_success(provider):
    """Test playlist search with mocked yt-dlp response."""
    mock_entries = [
        {
            "_type": "playlist",
            "id": "PL123",
            "title": "Test Playlist 1",
            "uploader": "Test Channel",
            "url": "https://youtube.com/playlist?list=PL123"
        },
        {
            "_type": "url",
            "ie_key": "YoutubeTab",
            "id": "PL456",
            "title": "Test Playlist 2",
            "url": "https://youtube.com/playlist?list=PL456"
        },
        {
            "_type": "video",
            "id": "video1",
            "title": "Not a playlist"
        }
    ]
    
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = {"entries": mock_entries}
    
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        results = provider._execute_playlist_search("test query", max_results=5)
        
        assert len(results) == 2
        assert results[0]["id"] == "PL123"
        assert results[1]["id"] == "PL456"

def test_execute_playlist_search_fallback(provider):
    """Test fallback mechanism when URL search fails."""
    mock_ydl_instance = MagicMock()
    # First call raises Exception
    mock_ydl_instance.extract_info.side_effect = [Exception("Search URL failed"), {"entries": [{"_type": "playlist", "id": "fallback_pl"}]}]
    
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        results = provider._execute_playlist_search("test query", max_results=5)
        
        # Should have called extract_info twice (main + fallback)
        assert mock_ydl_instance.extract_info.call_count == 2
        assert len(results) == 1
        assert results[0]["id"] == "fallback_pl"
