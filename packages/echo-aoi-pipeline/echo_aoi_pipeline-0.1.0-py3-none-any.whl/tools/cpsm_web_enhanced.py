#!/usr/bin/env python3
"""Enhanced web interface with category-based navigation."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

sys.path.insert(0, str(Path(__file__).parent))
from cpsm_quiz import load_questions, Question, PROGRESS_FILE
from cpsm_report import load_progress
from cpsm_category_analyzer import CATEGORIES, categorize_question, analyze_category

app = FastAPI(title="CPSM Module 3 Study Tool - Enhanced")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve main page with category navigation."""
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPSM Module 3 - Category Explorer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
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

        /* Category Grid */
        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .category-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }
        .category-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .category-icon {
            font-size: 2.5em;
            margin-right: 15px;
        }
        .category-name {
            font-size: 1.3em;
            font-weight: 700;
            color: #333;
        }
        .category-count {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: auto;
        }
        .category-desc {
            color: #666;
            font-size: 0.95em;
            line-height: 1.5;
        }
        .category-concept {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-left: 3px solid #667eea;
            font-size: 0.9em;
            color: #555;
        }

        /* Category Detail View */
        .category-detail {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            display: none;
        }
        .category-detail.active {
            display: block;
        }
        .back-btn {
            background: #e9ecef;
            color: #333;
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .back-btn:hover {
            background: #dee2e6;
        }
        .summary-section {
            margin: 20px 0;
        }
        .summary-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        .stat-row {
            display: flex;
            gap: 20px;
            margin: 15px 0;
        }
        .stat-box {
            flex: 1;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        .approach-list, .trap-list {
            list-style: none;
        }
        .approach-list li, .trap-list li {
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }
        .approach-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
        }
        .trap-list li:before {
            content: "⚠";
            position: absolute;
            left: 0;
            color: #e74c3c;
        }
        .question-preview {
            background: #fffbf0;
            border: 2px solid #ffc107;
            padding: 18px;
            margin: 12px 0;
            border-radius: 8px;
            border-left: 5px solid #f57c00;
        }
        .question-preview h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-weight: 700;
            font-size: 0.95em;
        }
        .question-preview p {
            color: #222;
            font-size: 1em;
            font-weight: 500;
            line-height: 1.6;
        }
        .start-quiz-btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            margin-top: 20px;
        }
        .start-quiz-btn:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 CPSM Module 3 - Category Explorer</h1>
            <p class="subtitle">카테고리별 핵심 패턴 학습</p>
        </header>

        <!-- Category Grid -->
        <div id="category-grid" class="category-grid"></div>

        <!-- Category Detail View -->
        <div id="category-detail" class="category-detail">
            <button class="back-btn" onclick="showCategoryGrid()">← 카테고리 목록으로</button>
            <div id="detail-content"></div>
        </div>
    </div>

    <script>
        let allCategories = {};
        let allQuestions = [];

        async function loadData() {
            const [categories, questions] = await Promise.all([
                fetch('/api/categories').then(r => r.json()),
                fetch('/api/questions').then(r => r.json())
            ]);
            allCategories = categories;
            allQuestions = questions;

            renderCategoryGrid();
        }

        function renderCategoryGrid() {
            const grid = document.getElementById('category-grid');
            grid.innerHTML = Object.entries(allCategories).map(([name, data]) => `
                <div class="category-card" onclick="showCategoryDetail('${name}')">
                    <div class="category-header">
                        <span class="category-icon">${name.split(' ')[0]}</span>
                        <span class="category-name">${name.split(' ').slice(1).join(' ')}</span>
                        <span class="category-count">${data.count}문제</span>
                    </div>
                    <div class="category-desc">${data.description}</div>
                    <div class="category-concept">
                        💡 ${data.key_concept}
                    </div>
                </div>
            `).join('');
        }

        async function showCategoryDetail(categoryName) {
            const analysis = await fetch(`/api/category/${encodeURIComponent(categoryName)}`).then(r => r.json());

            const detail = document.getElementById('detail-content');
            detail.innerHTML = `
                <h2>${categoryName}</h2>

                <div class="stat-row">
                    <div class="stat-box">
                        <div class="stat-label">총 문제 수</div>
                        <div class="stat-value">${analysis.total}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">핵심 개념</div>
                        <div class="stat-value" style="font-size: 1.1em;">${allCategories[categoryName].key_concept}</div>
                    </div>
                </div>

                <div class="summary-section">
                    <h3>🎯 문제 풀이 전략</h3>
                    <ul class="approach-list">
                        ${analysis.approaches.map(a => `<li>${a}</li>`).join('')}
                    </ul>
                </div>

                <div class="summary-section">
                    <h3>⚠️ 자주 나오는 함정</h3>
                    <ul class="trap-list">
                        ${analysis.common_traps.map(t => `<li>${t}</li>`).join('')}
                    </ul>
                </div>

                <div class="summary-section">
                    <h3>📊 정답 분포</h3>
                    ${Object.entries(analysis.answer_distribution || {})
                        .sort((a, b) => b[1] - a[1])
                        .map(([ans, count]) => {
                            const pct = (count / analysis.total * 100).toFixed(1);
                            return `<div style="margin: 8px 0;">${ans}: ${count}개 (${pct}%)</div>`;
                        }).join('')}
                </div>

                <div class="summary-section">
                    <h3>📚 대표 문제</h3>
                    ${analysis.examples.map((q, i) => `
                        <div class="question-preview">
                            <h4>${i+1}. ${q.problem_id}</h4>
                            <p>${q.summary}</p>
                        </div>
                    `).join('')}
                </div>

                <button class="start-quiz-btn" onclick="startCategoryQuiz('${categoryName}')">
                    이 카테고리 퀴즈 시작하기
                </button>
            `;

            document.getElementById('category-grid').style.display = 'none';
            document.getElementById('category-detail').classList.add('active');
        }

        function showCategoryGrid() {
            document.getElementById('category-grid').style.display = 'grid';
            document.getElementById('category-detail').classList.remove('active');
        }

        function startCategoryQuiz(categoryName) {
            alert(`카테고리 퀴즈 기능은 다음 단계에서 추가됩니다.\\n\\n현재는 CLI에서:\\npython tools/cpsm_quiz.py -t "${categoryName}" -n 10`);
        }

        // Load data on page load
        loadData();
    </script>
</body>
</html>
    """


@app.get("/api/categories")
async def get_categories():
    """Return category overview."""
    questions = load_questions(Path("cpsm_module3_judgment_db.md"))

    category_counts = defaultdict(int)
    for q in questions:
        cats = categorize_question(q)
        for cat in cats:
            category_counts[cat] += 1

    result = {}
    for cat_name, cat_info in CATEGORIES.items():
        result[cat_name] = {
            "count": category_counts.get(cat_name, 0),
            "description": cat_info["description"],
            "key_concept": cat_info["key_concept"],
        }

    return JSONResponse(result)


@app.get("/api/category/{category_name}")
async def get_category_detail(category_name: str):
    """Return detailed analysis for a category."""
    questions = load_questions(Path("cpsm_module3_judgment_db.md"))
    analysis = analyze_category(questions, category_name)

    # Convert Question objects to dicts
    result = {
        "total": analysis["total"],
        "answer_distribution": analysis["answer_distribution"],
        "common_traps": analysis["common_traps"],
        "approaches": analysis["approaches"],
        "examples": [
            {
                "problem_id": q.problem_id,
                "summary": q.summary,
                "answer": q.answer,
            }
            for q in analysis["examples"]
        ],
    }

    return JSONResponse(result)


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


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 CPSM Module 3 Category Explorer")
    print("="*60)
    print("\n📡 Server: http://localhost:8001")
    print("💡 Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
