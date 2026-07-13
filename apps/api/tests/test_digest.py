"""Unit tests for digest compilation and template rendering."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.digest import DigestPayload, HotLeadDigestItem, WarmLeadDigestItem
from app.services.digest import DigestService


class TestDigestCompilation:
    """Tests for the digest compilation logic."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def sample_leads(self):
        """Create sample lead data for testing."""
        leads = []
        now = datetime.now(timezone.utc)
        
        # Create 5 leads with different scores
        for i in range(5):
            lead = MagicMock()
            lead.id = f"lead-{i}"
            lead.email = f"lead{i}@example.com"
            lead.first_name = f"First{i}"
            lead.last_name = f"Last{i}"
            lead.company = f"Company{i}"
            lead.job_title = "CEO"
            lead.status = "scored"
            lead.created_at = now - timedelta(hours=12)
            leads.append(lead)
        
        return leads
    
    @pytest.fixture
    def sample_scores(self):
        """Create sample composite scores for testing."""
        scores = [
            {"composite_score": 92.0, "overall_summary": "This lead shows exceptional fit based on their recent funding round and technology stack alignment with our solution.", "suggested_action": "Call immediately"},
            {"composite_score": 78.0, "overall_summary": "Strong potential candidate with clear interest signals and budget authority confirmed during last quarter.", "suggested_action": "Send demo"},
            {"composite_score": 55.0, "overall_summary": "Moderate interest shown through website visits and content downloads, needs further nurturing.", "suggested_action": "Nurture campaign"},
            {"composite_score": 42.0, "overall_summary": "Some alignment with our ICP but timing concerns and limited budget availability noted.", "suggested_action": "Follow up later"},
            {"composite_score": 25.0, "overall_summary": "Poor fit due to company size mismatch and no apparent pain points identified.", "suggested_action": "Disqualify"},
        ]
        return scores
    
    @pytest.mark.asyncio
    async def test_digest_segments_hot_leads(self, mock_db_session, sample_leads, sample_scores):
        """Test that leads with score >= 75 are segmented as hot."""
        # Mock the database query results
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [sample_leads[0], sample_leads[1]]  # Two hot leads
        
        mock_score_result = MagicMock()
        mock_score_result.scalars().first.side_effect = [
            MagicMock(**sample_scores[0]),
            MagicMock(**sample_scores[1])
        ]
        
        mock_db_session.execute = AsyncMock(side_effect=[mock_result, mock_score_result, mock_score_result])
        
        service = DigestService(mock_db_session)
        payload = await service.compile_digest()
        
        assert payload.hot_count == 2
        assert len(payload.hot_leads) == 2
        assert all(lead.composite_score >= 75 for lead in payload.hot_leads)
    
    @pytest.mark.asyncio
    async def test_digest_segments_warm_leads(self, mock_db_session, sample_leads, sample_scores):
        """Test that leads with 40 <= score < 75 are segmented as warm."""
        # Mock the database query results
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [sample_leads[2], sample_leads[3]]  # Two warm leads
        
        mock_score_result = MagicMock()
        mock_score_result.scalars().first.side_effect = [
            MagicMock(**sample_scores[2]),
            MagicMock(**sample_scores[3])
        ]
        
        mock_db_session.execute = AsyncMock(side_effect=[mock_result, mock_score_result, mock_score_result])
        
        service = DigestService(mock_db_session)
        payload = await service.compile_digest()
        
        assert payload.warm_count == 2
        assert len(payload.warm_leads) == 2
        assert all(40 <= lead.composite_score < 75 for lead in payload.warm_leads)
    
    @pytest.mark.asyncio
    async def test_digest_counts_cold_leads(self, mock_db_session, sample_leads, sample_scores):
        """Test that leads with score < 40 are counted but not included."""
        # Mock the database query results
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [sample_leads[4]]  # One cold lead
        
        mock_score_result = MagicMock()
        mock_score_result.scalars().first.return_value = MagicMock(**sample_scores[4])
        
        mock_db_session.execute = AsyncMock(side_effect=[mock_result, mock_score_result])
        
        service = DigestService(mock_db_session)
        payload = await service.compile_digest()
        
        assert payload.cold_count == 1
        assert len(payload.hot_leads) == 0
        assert len(payload.warm_leads) == 0
    
    @pytest.mark.asyncio
    async def test_digest_total_calculation(self, mock_db_session, sample_leads, sample_scores):
        """Test that total leads count is correct."""
        # Mock all 5 leads
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = sample_leads
        
        mock_score_result = MagicMock()
        mock_score_result.scalars().first.side_effect = [MagicMock(**score) for score in sample_scores]
        
        mock_db_session.execute = AsyncMock(side_effect=[mock_result] + [mock_score_result] * 5)
        
        service = DigestService(mock_db_session)
        payload = await service.compile_digest()
        
        assert payload.total_leads == 5
        assert payload.hot_count + payload.warm_count + payload.cold_count == 5


class TestTemplateRendering:
    """Tests for Jinja2 template rendering."""
    
    @pytest.fixture
    def sample_payload(self):
        """Create a sample digest payload for testing."""
        hot_lead = HotLeadDigestItem(
            id="lead-1",
            email="hot@example.com",
            first_name="John",
            last_name="Doe",
            company="Acme Corp",
            job_title="CEO",
            composite_score=92.0,
            status="scored",
            overall_summary="This lead shows exceptional fit based on their recent funding round and technology stack alignment.",
            suggested_action="Schedule a discovery call within 24 hours to discuss their expansion plans.",
            criteria_scores=[
                {"criteria_name": "icp_fit", "score": 9, "reasoning": "Perfect match", "confidence": 0.95},
                {"criteria_name": "buying_intent", "score": 8, "reasoning": "High intent signals", "confidence": 0.85},
                {"criteria_name": "authority", "score": 10, "reasoning": "Decision maker", "confidence": 0.99},
                {"criteria_name": "pain_need", "score": 9, "reasoning": "Clear pain points", "confidence": 0.90},
                {"criteria_name": "timing", "score": 9, "reasoning": "Urgent timeline", "confidence": 0.88},
            ]
        )
        
        warm_lead = WarmLeadDigestItem(
            id="lead-2",
            email="warm@example.com",
            first_name="Jane",
            last_name="Smith",
            company="Beta Inc",
            job_title="CTO",
            composite_score=55.0,
            status="scored"
        )
        
        return DigestPayload(
            run_date=datetime.now(timezone.utc),
            total_leads=3,
            hot_count=1,
            warm_count=1,
            cold_count=1,
            hot_leads=[hot_lead],
            warm_leads=[warm_lead]
        )
    
    def test_template_renders_without_error(self, sample_payload):
        """Test that the template renders without throwing exceptions."""
        from jinja2 import Environment, FileSystemLoader
        from pathlib import Path
        
        template_dir = Path(__file__).parent.parent / "app" / "templates"
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        template = env.get_template("digest_email.html")
        
        # Should not raise an exception
        html = template.render(
            run_date=sample_payload.run_date,
            total_leads=sample_payload.total_leads,
            hot_count=sample_payload.hot_count,
            warm_count=sample_payload.warm_count,
            cold_count=sample_payload.cold_count,
            hot_leads=sample_payload.hot_leads,
            warm_leads=sample_payload.warm_leads
        )
        
        assert html is not None
        assert len(html) > 0
    
    def test_template_contains_expected_content(self, sample_payload):
        """Test that rendered template contains expected company names and scores."""
        from jinja2 import Environment, FileSystemLoader
        from pathlib import Path
        
        template_dir = Path(__file__).parent.parent / "app" / "templates"
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        template = env.get_template("digest_email.html")
        
        html = template.render(
            run_date=sample_payload.run_date,
            total_leads=sample_payload.total_leads,
            hot_count=sample_payload.hot_count,
            warm_count=sample_payload.warm_count,
            cold_count=sample_payload.cold_count,
            hot_leads=sample_payload.hot_leads,
            warm_leads=sample_payload.warm_leads
        )
        
        # Check for expected content
        assert "Acme Corp" in html
        assert "Beta Inc" in html
        assert "John Doe" in html
        assert "92" in html  # Hot lead score
        assert "55" in html  # Warm lead score
        assert "Daily Lead Digest" in html


class TestSlackPayload:
    """Tests for Slack Block Kit payload generation."""
    
    def test_slack_payload_structure(self):
        """Test that generated Slack payload matches Block Kit schema."""
        from app.adapters.notifications.slack import SlackAdapter
        from app.schemas.digest import DigestPayload
        
        payload = DigestPayload(
            run_date=datetime.now(timezone.utc),
            total_leads=5,
            hot_count=2,
            warm_count=2,
            cold_count=1,
            hot_leads=[],
            warm_leads=[]
        )
        
        adapter = SlackAdapter(webhook_url="https://hooks.slack.com/test")
        block_kit = adapter._build_block_kit_payload(payload)
        
        # Verify structure
        assert "blocks" in block_kit
        assert isinstance(block_kit["blocks"], list)
        assert len(block_kit["blocks"]) > 0
        
        # First block should be header
        assert block_kit["blocks"][0]["type"] == "header"
        
        # Should have stats section
        has_stats = any(
            block.get("type") == "section" and "fields" in block
            for block in block_kit["blocks"]
        )
        assert has_stats
