# Generating Diagrams with AI

This document explains how we used AI to design the architecture for the application using the C4 model and UML diagrams.

## How we used the AI

The AI acted like a helpful assistant, turning the app's requirements into visual diagrams. Here is what it did:

* It generated the exact code needed for the `C4-PlantUML` library so we could easily view the diagrams.

* It helped group different parts of the app (like Next.js, FastAPI, and PostgreSQL) into clear containers and components.

* It suggested splitting the Level 4 Class Diagrams into three separate ones so they wouldn't be too crowded and hard to read.

## How the process went

Working with the AI was a step-by-step conversation:

* We started with the big picture (Level 1 Context) and slowly zoomed in through Level 2 (Containers), Level 3 (Components), and finally Level 4 (Class Diagrams).

* After writing the code for a diagram, the AI always added a short guide explaining its choices, like why the Web Speech API was placed in the browser instead of the backend.

* At one point, the PlantUML editor threw an error because some lines of code were split. The AI quickly figured out the issue and gave us the corrected code.

ChatGPT Conversation URL: https://chatgpt.com/share/6ad4c0fb-339c-83ed-a843-2cf884bc0669