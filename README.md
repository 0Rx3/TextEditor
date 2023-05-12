# Block-based text editor
## Hypothesis:
* MS Word's approach of styling isn't friendly for the user because of style disappearance on deletion/insertion. 
* MS Word's implementation of lists starts being a problem when the depth reaches 3+. 
* A better implementation can be made.
## Features:
* User friendly minimalistic interface
   1. Free of usually unneeded styling option like font color
   1. Easy to reach options
   1. Easy management of styles
* Exports
   1. To .pdf (which can be used to create a .docx)
   1. To .md
* Block-based styling approach:
   1. Makes sure that any style that the user creates will be preserved at any point of the time
   1. Makes it easier to edit multiple separate paragraphs with the same style
## Main issues:
* Lists are poorly optimized.
* Most of the updates are done "onCursorMove"
## Synopsis:
* Before reaching this poin there were many iterations:
   1. React-js 1: tried to refactor and couldn't do it (10-14 days):
      * Input was done via contenteditables;
      * Callbacks were a pain when reaching a depth of 3;
      * Poor architecture has lead to a restart;
   1. C/C++ Qt 1 (3-5 days):
      * Main idea was to mimic first iteration;
      * It meant that any enter press leads to a creation of a new QTextEdit and so on;
   1. C/C++ Qt 2 (5-7 days):
      * This iteration was made in an attempt to write something from scratch;
      * Couldn't actually create a custom QTextBlock + QTextDocument and needed to stop;
   1. Angular (5-7 days):
      * Backtracked to contenteditables;
      * Couldn't use them correctly. Stopped after implementing when reached about the same progress as in first iteration.
   1. React-js 2 (10-14 days):
      * Basically a redo of the first iteration but instead of contenteditables used a switch from <p> to <textarea> on click.
      * Couldn't create:
         * Lists relationship with inheritance of previous numbers
         * Export to docx (stopped because of it)
   1. React-js 3 (1-2 days):
      * Redo of React-js 2 with an attempt to use ContentEditable library
   1. Python Qt (14 days+):
      * Current iteration
      * Actually managed to create lists, exports and fixed most of the problems connected to styling
## Skills and knowledge acquired:
* Understanding of event based programming.
* Intermediate-level work with PyQt library.
* First experience of creating an actual app.
* Some knowledge of React-JS and Angular
