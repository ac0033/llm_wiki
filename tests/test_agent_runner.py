"""知识库模型分工与失败停点；不调用真实 CLI。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from service import agent_runner
from service.agent_cli import AgentReply, AgentError


def test_single_fenced_json_is_accepted_but_prose_is_not():
    assert agent_runner.structured_result('```json\n{"sources":[]}\n```') == {"sources": []}
    for text in ('说明\n{"sources":[]}', '[]', '{"sources":[]}\n完成'):
        with pytest.raises(ValueError):
            agent_runner.structured_result(text)


def test_query_has_no_write_permission(monkeypatch):
    def invoke(provider, model, prompt, **kwargs):
        assert provider == "claude"
        assert model == "claude-opus-5"
        assert kwargs["writable"] == ()
        assert "先真实调用 memory_context" in prompt
        assert "mcp__agent-memory__memory_context" in kwargs["mcp_tools"]
        assert "mcp__agent-memory__memory_add" not in kwargs["mcp_tools"]
        return AgentReply("回答", model, model)
    monkeypatch.setattr(agent_runner, "invoke", invoke)
    assert "回答" in agent_runner.run_agent("query", "问题")


def test_ingest_write_paths_are_limited(monkeypatch):
    def invoke(provider, model, prompt, **kwargs):
        assert kwargs["writable"] == ("./wiki/**",)
        assert model == "claude-opus-5"
        return AgentReply("完成", model, model)
    monkeypatch.setattr(agent_runner, "invoke", invoke)
    agent_runner.run_agent("ingest", "入库")


def test_batch_never_grants_human_review_or_delete_tools():
    from service.memory_config import settings, instructions
    tools = settings(agent_runner.ROOT, writing=True)["mcp_tools"]
    assert "mcp__agent-memory__memory_add" in tools
    for forbidden in ("memory_review_resolve", "memory_forget", "memory_update", "memory_wm_clear"):
        assert not any(tool.endswith("__" + forbidden) for tool in tools)
    assert "不设置 acknowledge_pending" in instructions(agent_runner.ROOT)


def test_memory_disabled_does_not_send_mcp_config(monkeypatch):
    monkeypatch.setenv("KB_MEMORY_ENABLED", "0")
    def invoke(provider, model, prompt, **kwargs):
        assert "mcp_config" not in kwargs
        assert "未连接 agent-memory" in prompt
        return AgentReply("无记忆", model, model)
    monkeypatch.setattr(agent_runner, "invoke", invoke)
    agent_runner.run_agent("query", "问题")


@pytest.mark.parametrize("text", ['完成了', '{"verdict":"fail","issues":["缺来源"],"checked":["a"]}',
                                     '{"verdict":"pass","issues":[],"checked":[]}'])
def test_audit_cannot_pass_without_evidence(monkeypatch, tmp_path, text):
    monkeypatch.setattr(agent_runner, "ROOT", tmp_path)
    monkeypatch.setattr(agent_runner, "audit_bundle", lambda changed: '{"pages":[],"raw_sources":[]}')
    monkeypatch.setattr(agent_runner, "invoke", lambda *a, **k: AgentReply(text, "", ""))
    with pytest.raises(AgentError):
        agent_runner.audit("任务")


def test_audit_requires_all_changed_pages(monkeypatch, tmp_path):
    monkeypatch.setattr(agent_runner, "ROOT", tmp_path)
    monkeypatch.setattr(agent_runner, "audit_bundle", lambda changed: '{"test":"完整测试材料"}')
    monkeypatch.setattr(agent_runner, "invoke", lambda *a, **k: AgentReply(
        '{"verdict":"pass","issues":[],"checked":["wiki/a.md"]}', "", ""))
    with pytest.raises(AgentError):
        agent_runner.audit("任务", ["wiki/a.md", "wiki/b.md"])


def test_audit_bundle_reads_only_linked_raw_and_preserves_text(monkeypatch, tmp_path):
    import json
    monkeypatch.setattr(agent_runner, "ROOT", tmp_path)
    for folder in ('wiki/papers','raw/articles','data/registry'):
        (tmp_path/folder).mkdir(parents=True)
    (tmp_path/'wiki/papers/source.md').write_text('依据 https://example.com/a',encoding='utf-8')
    (tmp_path/'raw/articles/source.md').write_text('原文：Step 0 到 Step 8。',encoding='utf-8')
    (tmp_path/'raw/articles/unrelated.md').write_text('无关内容不得传出',encoding='utf-8')
    (tmp_path/'data/registry/ingested.jsonl').write_text(json.dumps(
        {'slug':'source','url':'https://example.com/a','source':'url'}),encoding='utf-8')
    bundle=agent_runner.audit_bundle(['wiki/papers/source.md'])
    assert '原文：Step 0 到 Step 8。' in bundle
    assert '无关内容不得传出' not in bundle
    with pytest.raises(AgentError):
        agent_runner.audit_bundle(['../outside.md'])
