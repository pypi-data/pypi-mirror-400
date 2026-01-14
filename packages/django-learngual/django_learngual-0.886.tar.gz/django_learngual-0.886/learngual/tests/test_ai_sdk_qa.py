from iam_service.utilities.utils import TestHelper

from ..ai_sdk import AIProcessing


class TestAIProcessingQA(TestHelper):
    def test_qa_generate_live_shape(self):
        qa_generate_payload = {
            "passage": (
                "The solar system consists of the Sun and the objects that orbit it, "
                "including eight planets, their moons, dwarf planets, and countless small "
                "bodies like asteroids and comets. The Sun is at the center, and the planets "
                "orbit in elliptical paths."
            ),
            "questions": [
                {"id": "q1", "prompt": "What is at the center of the solar system?"},
                {
                    "id": "q2",
                    "prompt": "How many planets are there in the solar system?",
                },
                {
                    "id": "q3",
                    "prompt": "What types of objects orbit the Sun besides planets?",
                },
            ],
            "question_set_id": "quiz-set-123",
            "test_id": "test-456",
            "context_label": "Science Education",
            "query_string": None,
        }

        result = AIProcessing.qa_generate(
            passage=qa_generate_payload["passage"],
            questions=qa_generate_payload["questions"],
            question_set_id=qa_generate_payload["question_set_id"],
            test_id=qa_generate_payload["test_id"],
            context_label=qa_generate_payload["context_label"],
            query_string=qa_generate_payload["query_string"],
        )

        # if not result.get("status"):
        #     pytest.skip("QA generate live endpoint unavailable or unauthorized")
        assert result.get("status") is True, "QA generate request failed"
        resp_json = result["response"].json()
        assert self.has_fields(
            resp_json,
            ["questionSetId", "passageVersion", "answers", "passageHash", "createdAt"],
        )
        assert isinstance(resp_json.get("answers"), list)
        if resp_json["answers"]:
            first = resp_json["answers"][0]
            # metrics may be absent per docs; check core fields
            assert self.has_fields(
                first,
                ["id", "prompt", "answer", "explanation", "cached"],
            )

    def test_qa_generate_and_evaluate_live_shape(self):
        # First generate canonical answers
        gen_payload = {
            "passage": (
                "The solar system consists of the Sun and the objects that orbit it, "
                "including eight planets, their moons, dwarf planets, and countless small "
                "bodies like asteroids and comets. The Sun is at the center, and the planets "
                "orbit in elliptical paths."
            ),
            "questions": [
                {"id": "q1", "prompt": "What is at the center of the solar system?"},
                {
                    "id": "q2",
                    "prompt": "How many planets are there in the solar system?",
                },
            ],
            "question_set_id": "quiz-set-123",
            "test_id": "test-456",
            "context_label": None,
        }

        gen = AIProcessing.qa_generate(
            passage=gen_payload["passage"],
            questions=gen_payload["questions"],
            question_set_id=gen_payload["question_set_id"],
            test_id=gen_payload["test_id"],
            context_label=gen_payload["context_label"],
        )

        gen_json = gen["response"].json()
        question_set_id = gen_json.get("questionSetId")
        passage_version = gen_json.get("passageVersion")

        # Then evaluate student answers
        answers = [
            {
                "id": "q1",
                "response": "The Sun is at the center.",
                "audioUrl": None,
            },
            {
                "id": "q2",
                "response": "There are eight planets.",
                "audioUrl": None,
            },
        ]

        ev = AIProcessing.qa_evaluate(
            answers=answers,
            passage_version=passage_version,
            question_set_id=question_set_id,
            test_id=gen_payload["test_id"],
        )
        assert ev.get("status") is True, "QA evaluate request failed"
        ev_json = ev["response"].json()
        assert self.has_fields(
            ev_json,
            ["questionSetId", "passageVersion", "results", "evaluatedAt"],
        )
        assert isinstance(ev_json.get("results"), list)
        if ev_json["results"]:
            first = ev_json["results"][0]
            assert self.has_fields(
                first,
                ["id", "correct", "confidence", "feedback", "usedLlm"],
            )
            # Confidence should be between 0 and 1 per docs
            conf = first.get("confidence")
            if isinstance(conf, (int, float)):
                assert 0 <= float(conf) <= 1
