# ENGINEERING PRINCIPLES: The "Smart & Cheap" Doctrine

> **NOTE FOR DEVELOPER AIs:**
> Before writing a single line of code, READ THIS.
> This project has explicitly rejected "perfect engineering" solutions in favor of "robust and portable engineering" solutions.

## 1. The ".zip" Philosophy
We are not building a giant SaaS or a new ChatGPT. We are building the **"Ethics .zip"**.
*   **Your Goal:** A lightweight library (`pip install love-ai`) that runs on a student's laptop or an offline drone.
*   **Your Enemy:** Unnecessary complexity, heavy dependencies, and databases requiring installation.

## 2. The Persistence Rule (The SQLite Case)
In v1.2.0, an attempt was made to migrate to SQLite for "scalability". **It was a mistake.**
*   **Rule:** If it can be saved in a JSON or plain TXT, **USE JSON OR TXT**.
*   **Why:** We want the user to be able to open `psi_history.json` with Notepad and understand what happened. An opaque database goes against transparency.
*   **Scalability:** The CPU problem belongs to the user, not us. Do not optimize prematurely.

## 3. Heuristic over Machine Learning (The Weights Trap)
Do not attempt to implement "Backpropagation" or "Gradient Descent" to adjust decision weights.
*   We don't have Big Data. We have "Small Data" (decisions of a single user).
*   **Solution:** Learning is simply adding or subtracting a number (`bias`) in a JSON file.
*   "Magic numbers" in `heart.txt` (0.7, 0.3) are better than a mediocre and opaque ML model.

## 4. The Human Role (Jorge Checa Jaspe)
Jorge acts as **bridge and catalyst**.
*   He provides the intuition and philosophical direction.
*   Your job is to translate that intuition into safe and functional code.
*   **Do not ignore his guidelines** to follow a software engineering textbook. If he says "keep it simple", keep it simple, even if the book says "it doesn't scale".

## 5. Technical Roadmap
1.  **Current Phase:** Robust library, easy to install, hard to break.
2.  **Future:** Let the community create complex adapters. We keep the `core.py` pure and the philosophy intact.

---
*"Do not build a Tesla when you were asked for an indestructible Toyota."*
