from biocframe import BiocFrame

from experimenthub.registry import ExperimentHubRegistry


def test_real():
    ehub = ExperimentHubRegistry()
    assert len(ehub.list_ids()) > 0

    ehub_id = "EH4663"
    rec = ehub.get_record(ehub_id)
    assert rec is not None
    assert rec.ehub_id == ehub_id

    data = ehub.load(ehub_id)
    assert isinstance(data, BiocFrame)
    assert len(data) == 8425
