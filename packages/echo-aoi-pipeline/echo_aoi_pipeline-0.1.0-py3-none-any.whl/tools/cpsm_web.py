#!/usr/bin/env python3
"""Simple web interface for CPSM Module 3 study tool."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).parent))
from cpsm_quiz import load_questions, Question, PROGRESS_FILE
from cpsm_report import load_progress

app = FastAPI(title="CPSM Module 3 Study Tool")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve main page."""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPSM Module 3 Study Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .question-item {
            padding: 18px;
            margin: 12px 0;
            background: white;
            border: 2px solid #e9ecef;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .question-item:hover {
            border-color: #667eea;
            background: #f8f9ff;
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
        }
        .question-id {
            font-weight: 700;
            color: #667eea;
            margin-bottom: 8px;
            font-size: 0.95em;
        }
        .question-summary {
            color: #333;
            font-size: 1em;
            font-weight: 500;
            line-height: 1.5;
        }
        .tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-top: 5px;
        }
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }
        .btn:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }
        .filter-group {
            margin-bottom: 20px;
        }
        .filter-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 600;
        }
        .filter-group select, .filter-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            width: 90%;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .close-btn {
            font-size: 1.5em;
            cursor: pointer;
            color: #999;
        }
        .close-btn:hover {
            color: #333;
        }
        .quiz-question {
            background: #fff9e6;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 25px;
            margin: 15px 0;
        }
        .quiz-question p strong {
            font-size: 1.1em;
            color: #333;
            line-height: 1.6;
        }
        .quiz-options {
            margin-top: 15px;
        }
        .option-btn {
            display: block;
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
            font-size: 1.02em;
            line-height: 1.5;
        }
        .option-btn strong {
            color: #667eea;
            font-size: 1.1em;
            margin-right: 8px;
        }
        .option-btn:hover {
            border-color: #667eea;
            background: #f0f4ff;
            transform: translateX(5px);
        }
        .option-btn.correct {
            border-color: #27ae60;
            background: #d4edda;
        }
        .option-btn.incorrect {
            border-color: #e74c3c;
            background: #f8d7da;
        }
        .option-btn:disabled {
            cursor: not-allowed;
            opacity: 0.7;
        }
        .rationale {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 15px;
            border-radius: 4px;
        }
        .quiz-progress {
            text-align: center;
            margin-bottom: 15px;
            color: #666;
            font-weight: 600;
        }
        .quiz-result {
            text-align: center;
            padding: 30px;
        }
        .quiz-result h3 {
            font-size: 2em;
            color: #667eea;
            margin-bottom: 10px;
        }
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 CPSM Module 3 Study Tool</h1>
            <p class="subtitle">Interactive Learning & Progress Tracking</p>
        </header>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-questions">-</div>
                <div class="stat-label">Total Questions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="attempted">-</div>
                <div class="stat-label">Attempted</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="accuracy">-</div>
                <div class="stat-label">Accuracy</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2>📋 Question Bank</h2>
                <div class="filter-group">
                    <label>Filter by Tag</label>
                    <select id="tag-filter" onchange="filterQuestions()">
                        <option value="">All Tags</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Search</label>
                    <input type="text" id="search-box" placeholder="Search questions..." oninput="filterQuestions()">
                </div>
                <div id="questions-list"></div>
            </div>

            <div class="card">
                <h2>🎯 Quick Start</h2>
                <button class="btn" onclick="startQuiz(5)" style="width: 100%; margin-bottom: 10px;">
                    Start Random Quiz (5 questions)
                </button>
                <button class="btn" onclick="startQuiz(10)" style="width: 100%; margin-bottom: 10px;">
                    Start Random Quiz (10 questions)
                </button>
                <button class="btn" onclick="reviewWeak()" style="width: 100%; background: #e74c3c;">
                    Review Weak Areas
                </button>
            </div>
        </div>
    </div>

    <div id="modal" class="modal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h2 id="modal-title"></h2>
                <span class="close-btn" onclick="closeModal()">&times;</span>
            </div>
            <div id="modal-body"></div>
        </div>
    </div>

    <script>
        let allQuestions = [];
        let allProgress = [];

        async function loadData() {
            const [questions, progress] = await Promise.all([
                fetch('/api/questions').then(r => r.json()),
                fetch('/api/progress').then(r => r.json())
            ]);
            allQuestions = questions;
            allProgress = progress;

            updateStats();
            populateTagFilter();
            renderQuestions(allQuestions);
        }

        function updateStats() {
            const attempted = new Set(allProgress.map(p => extractCode(p.problem_id))).size;
            const correct = allProgress.filter(p => p.correct).length;
            const accuracy = allProgress.length > 0 ? (correct / allProgress.length * 100).toFixed(1) : 0;

            document.getElementById('total-questions').textContent = allQuestions.length;
            document.getElementById('attempted').textContent = attempted;
            document.getElementById('accuracy').textContent = accuracy + '%';
        }

        function extractCode(problemId) {
            const match = problemId.match(/LB\\d+/);
            return match ? match[0] : problemId;
        }

        function populateTagFilter() {
            const tags = new Set();
            allQuestions.forEach(q => {
                q.tags.split(',').forEach(tag => tags.add(tag.trim()));
            });

            const select = document.getElementById('tag-filter');
            Array.from(tags).sort().forEach(tag => {
                const option = document.createElement('option');
                option.value = tag;
                option.textContent = tag;
                select.appendChild(option);
            });
        }

        function filterQuestions() {
            const tag = document.getElementById('tag-filter').value;
            const search = document.getElementById('search-box').value.toLowerCase();

            let filtered = allQuestions;

            if (tag) {
                filtered = filtered.filter(q => q.tags.includes(tag));
            }

            if (search) {
                filtered = filtered.filter(q =>
                    q.summary.toLowerCase().includes(search) ||
                    q.problem_id.toLowerCase().includes(search)
                );
            }

            renderQuestions(filtered);
        }

        function renderQuestions(questions) {
            const list = document.getElementById('questions-list');
            list.innerHTML = questions.map(q => `
                <div class="question-item" onclick="showQuestion('${q.entry_id}')">
                    <div class="question-id">${q.problem_id}</div>
                    <div class="question-summary">${q.summary.substring(0, 100)}...</div>
                    <div>${q.tags.split(',').map(tag =>
                        '<span class="tag">' + tag.trim() + '</span>'
                    ).join('')}</div>
                </div>
            `).join('');
        }

        function showQuestion(entryId) {
            const question = allQuestions.find(q => q.entry_id === entryId);
            if (!question) return;

            document.getElementById('modal-title').textContent = question.problem_id;
            document.getElementById('modal-body').innerHTML = `
                <div style="background: #fffbf0; border: 2px solid #ffc107; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 0.9em; color: #f57c00; font-weight: 600; margin-bottom: 10px;">📝 문제</div>
                    <p style="font-size: 1.15em; font-weight: 600; color: #222; line-height: 1.7; margin: 0;">${question.summary}</p>
                </div>

                <div style="background: #f8f9fa; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 0.9em; color: #666; font-weight: 600; margin-bottom: 10px;">📋 보기</div>
                    <div style="color: #333; line-height: 1.7;">${question.options}</div>
                </div>

                <div style="background: #d4edda; border-left: 4px solid #27ae60; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 0.9em; color: #27ae60; font-weight: 600; margin-bottom: 10px;">✅ 정답</div>
                    <div style="font-weight: 600; color: #155724;">${question.answer}</div>
                </div>

                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 0.9em; color: #f57c00; font-weight: 600; margin-bottom: 10px;">💡 판별 근거</div>
                    <div style="color: #333; line-height: 1.7;">${question.rationale}</div>
                </div>

                <div style="margin-top: 15px;">
                    <div style="font-size: 0.9em; color: #666; font-weight: 600; margin-bottom: 10px;">🏷️ 태그</div>
                    ${question.tags.split(',').map(tag =>
                        '<span class="tag">' + tag.trim() + '</span>'
                    ).join('')}
                </div>
            `;
            document.getElementById('modal').style.display = 'block';
        }

        function closeModal(event) {
            if (!event || event.target.id === 'modal') {
                document.getElementById('modal').style.display = 'none';
            }
        }

        let currentQuiz = [];
        let currentQuestionIndex = 0;
        let quizResults = [];
        let questionStartTime = null;

        function startQuiz(count) {
            // Randomly sample questions
            const shuffled = [...allQuestions].sort(() => Math.random() - 0.5);
            currentQuiz = shuffled.slice(0, Math.min(count, shuffled.length));
            currentQuestionIndex = 0;
            quizResults = [];

            showQuizQuestion();
        }

        function reviewWeak() {
            // Find questions with low accuracy
            const lastAttempts = {};
            allProgress.forEach(p => {
                const code = extractCode(p.problem_id);
                lastAttempts[code] = p.correct;
            });

            const weakQuestions = allQuestions.filter(q => {
                const code = extractCode(q.problem_id);
                return lastAttempts[code] === false || !lastAttempts[code];
            });

            if (weakQuestions.length === 0) {
                alert('No weak areas found! Try taking more quizzes first.');
                return;
            }

            currentQuiz = weakQuestions.slice(0, Math.min(5, weakQuestions.length));
            currentQuestionIndex = 0;
            quizResults = [];

            showQuizQuestion();
        }

        function showQuizQuestion() {
            if (currentQuestionIndex >= currentQuiz.length) {
                showQuizResults();
                return;
            }

            const q = currentQuiz[currentQuestionIndex];
            questionStartTime = Date.now();

            document.getElementById('modal-title').textContent =
                `Question ${currentQuestionIndex + 1} / ${currentQuiz.length}`;

            document.getElementById('modal-body').innerHTML = `
                <div class="quiz-progress">
                    Progress: ${currentQuestionIndex + 1} / ${currentQuiz.length}
                </div>
                <div style="background: #e9ecef; padding: 8px 12px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9em; color: #666;">
                    🆔 ${q.problem_id}
                </div>
                <div class="quiz-question">
                    <div style="background: #fffbf0; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        <div style="font-size: 0.85em; color: #f57c00; font-weight: 600; margin-bottom: 8px;">📝 문제</div>
                        <p style="font-size: 1.15em; font-weight: 600; color: #222; line-height: 1.7; margin: 0;">${q.summary}</p>
                    </div>
                    <div class="quiz-options" id="quiz-options">
                        ${renderQuizOptions(q)}
                    </div>
                </div>
            `;

            document.getElementById('modal').style.display = 'block';
        }

        function parseOptions(optionText) {
            // Try to split by number patterns: "1) ... 2) ..." or "(A) ... (B) ..."
            const patterns = [
                /\s+(?=\d+\))/,           // "1) ... 2) ..."
                /\s+(?=\([A-D]\))/,       // "(A) ... (B) ..."
            ];

            for (const pattern of patterns) {
                const split = optionText.split(pattern).filter(s => s.trim());
                if (split.length >= 2) {
                    return split.map(opt => opt.trim());
                }
            }

            // Fallback: return as single option
            return [optionText.trim()];
        }

        function normalizeOptionNumber(optionText) {
            // Extract number from "1) ..." or "(A) ..." and return normalized index
            const match = optionText.match(/^(\d+)\)/) || optionText.match(/^\(([A-D])\)/);
            if (!match) return null;

            const num = match[1];
            // Convert A,B,C,D to 1,2,3,4
            if (/[A-D]/.test(num)) {
                return String(num.charCodeAt(0) - 'A'.charCodeAt(0) + 1);
            }
            return num;
        }

        function renderQuizOptions(question) {
            const options = parseOptions(question.options);

            return options.map((opt, idx) => {
                const displayNum = idx + 1;
                const originalNum = normalizeOptionNumber(opt) || String(displayNum);

                // Clean display text (remove leading number/letter)
                let displayText = opt.replace(/^(\d+\)|\([A-D]\))\s*/, '');

                return `
                    <button class="option-btn" data-answer="${originalNum}" onclick="submitAnswer('${originalNum}', this)">
                        <strong>${displayNum}.</strong> ${displayText}
                    </button>
                `;
            }).join('');
        }

        function normalizeAnswer(answerText) {
            // Extract answer from "1번 –" or "(A) –" or just "1" or "A"
            const match = answerText.match(/^(\d+)번?/) || answerText.match(/^\(?([A-D])\)?/);
            if (!match) return '';

            const ans = match[1];
            // Convert A,B,C,D to 1,2,3,4
            if (/[A-D]/.test(ans)) {
                return String(ans.charCodeAt(0) - 'A'.charCodeAt(0) + 1);
            }
            return ans;
        }

        async function submitAnswer(userAnswer, button) {
            const q = currentQuiz[currentQuestionIndex];
            const timeSpent = (Date.now() - questionStartTime) / 1000;

            // Extract correct answer number (normalize both formats)
            const correctAnswer = normalizeAnswer(q.answer);

            const isCorrect = userAnswer === correctAnswer;

            // Record result
            quizResults.push({
                problem_id: q.problem_id,
                correct: isCorrect,
                time_spent: timeSpent,
                user_answer: userAnswer
            });

            // Save to backend
            await fetch('/api/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    problem_id: q.problem_id,
                    correct: isCorrect,
                    time_spent: timeSpent,
                    user_answer: userAnswer
                })
            });

            // Show feedback
            const allButtons = document.querySelectorAll('.option-btn');
            allButtons.forEach(btn => btn.disabled = true);

            if (isCorrect) {
                button.classList.add('correct');
            } else {
                button.classList.add('incorrect');
                // Highlight correct answer by matching data-answer attribute
                allButtons.forEach(btn => {
                    if (btn.getAttribute('data-answer') === correctAnswer) {
                        btn.classList.add('correct');
                    }
                });
            }

            // Show rationale
            document.getElementById('modal-body').innerHTML += `
                <div class="rationale">
                    <strong>${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</strong><br>
                    <strong>Answer:</strong> ${q.answer}<br><br>
                    <strong>Rationale:</strong><br>${q.rationale}
                </div>
                <button class="btn" onclick="nextQuestion()" style="margin-top: 20px; width: 100%;">
                    ${currentQuestionIndex + 1 < currentQuiz.length ? 'Next Question' : 'See Results'}
                </button>
            `;
        }

        function nextQuestion() {
            currentQuestionIndex++;
            showQuizQuestion();
        }

        function showQuizResults() {
            const correct = quizResults.filter(r => r.correct).length;
            const total = quizResults.length;
            const percentage = (correct / total * 100).toFixed(1);

            document.getElementById('modal-title').textContent = 'Quiz Complete!';
            document.getElementById('modal-body').innerHTML = `
                <div class="quiz-result">
                    <h3>${percentage}%</h3>
                    <p style="font-size: 1.2em; margin: 20px 0;">
                        You got <strong>${correct}</strong> out of <strong>${total}</strong> correct!
                    </p>
                    <button class="btn" onclick="closeModal(); loadData();" style="margin-top: 20px;">
                        Close & Refresh Stats
                    </button>
                </div>
            `;
        }

        // Load data on page load
        loadData();
    </script>
</body>
</html>
    """


@app.get("/api/questions")
async def get_questions():
    """Return all questions as JSON."""
    questions = load_questions(Path("cpsm_module3_judgment_db.md"))
    return JSONResponse([
        {
            "entry_id": q.entry_id,
            "problem_id": q.problem_id,
            "summary": q.summary,
            "options": q.options,
            "answer": q.answer,
            "rationale": q.rationale,
            "tags": q.tags,
        }
        for q in questions
    ])


@app.get("/api/progress")
async def get_progress():
    """Return progress data as JSON."""
    return JSONResponse(load_progress())


@app.post("/api/submit")
async def submit_answer(request: Request):
    """Save quiz result to progress file."""
    from datetime import datetime

    data = await request.json()

    # Create result entry
    result = {
        "problem_id": data["problem_id"],
        "date": datetime.now().isoformat(),
        "correct": data["correct"],
        "time_spent": data["time_spent"],
        "user_answer": data["user_answer"]
    }

    # Append to progress file
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS_FILE.open("a", encoding="utf-8") as f:
        import json
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return JSONResponse({"status": "ok", "result": result})


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 CPSM Module 3 Web Interface")
    print("="*60)
    print("\n📡 Server: http://localhost:8000")
    print("💡 Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
