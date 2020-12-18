from PyQt5.Qsci import (
	QsciLexerFortran,
)
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import *


def createCodeEditor(initial):
	editor = QsciScintilla()
	"""
	Customization - GENERAL
	"""
	# # Disable the lexer
	editor.setLexer(QsciLexerFortran())
	# # Set the encoding to UTF-8
	# editor.setUtf8(True)
	# # Set the tab width to 4 spaces
	# editor.setTabWidth(2)
	# # Set the End-Of-Line character to Unix style ('\n')
	# editor.setEolMode(QsciScintilla.EolUnix)
	# # Make End-Of-Line characters visible
	# # editor.setEolVisibility(True)
	# # Set the zoom factor, the factor is in points.
	# editor.zoomTo(4)
	#
	# """
	# Customization - LINE WRAPPING
	# """
	# # Set the text wrapping mode to word wrap
	# editor.setWrapMode(QsciScintilla.WrapWord)
	# # Set the text wrapping mode visual indication
	# editor.setWrapVisualFlags(
	# 	QsciScintilla.WrapFlagByText, QsciScintilla.WrapFlagByText
	# )
	# # Set the text wrapping to indent the wrapped lines
	# editor.setWrapIndentMode(QsciScintilla.WrapIndentSame)
	#
	# """
	# Customization - EDGE MARKER
	# """
	# # Set the edge marker's position and set it to color the background
	# # when a line goes over the limit of 50 characters
	# # editor.setEdgeMode(QsciScintilla.EdgeBackground)
	# # editor.setEdgeColumn(40)
	# edge_color = caret_fg_color = QColor("#ff00ff00")
	# # editor.setEdgeColor(edge_color)
	# # Add a long line that will display the edge marker coloring
	#
	# """
	# Customization - INDENTATION
	# """
	# # Set indentation with spaces instead of tabs
	# # editor.setIndentationsUseTabs(False)
	# # Set the tab width to 4 spaces
	# editor.setTabWidth(2)
	# # Set tab indent mode, see the 3.3.3 chapter in QSciDocs
	# # for a detailed explanation
	# # editor.setTabIndents(True)
	# # Set autoindentation mode to maintain the indentation level of the previous line
	# # (the editor's lexer HAS to be disabled)
	# # editor.setAutoIndent(True)
	# # Make the backspace jump back to the tab width guides instead of deleting
	# # one character, but only when there are ONLY whitespaces on the left side of the cursor
	# # editor.setBackspaceUnindents(True)
	# # Set indentation guides to be visible
	# # editor.setIndentationGuides(True)
	#
	# """
	# Customization - CARET (the blinking cursor indicator)
	# """
	# # Set the caret color to red
	# caret_fg_color = QColor("#ffff0000")
	# editor.setCaretForegroundColor(caret_fg_color)
	# # Enable and set the caret line background color to slightly transparent blue
	# editor.setCaretLineVisible(True)
	# caret_bg_color = QColor("#1f0000ff")
	# editor.setCaretLineBackgroundColor(caret_bg_color)
	# # Set the caret width of 4 pixels
	# # editor.setCaretWidth(4)
	#
	# """
	# Customization - AUTOCOMPLETION (Partially usable without a lexer)
	# """
	# # Set the autocompletions to case INsensitive
	# editor.setAutoCompletionCaseSensitivity(False)
	# # Set the autocompletion to not replace the word to the right of the cursor
	# editor.setAutoCompletionReplaceWord(False)
	# # Set the autocompletion source to be the words in the document
	# editor.setAutoCompletionSource(QsciScintilla.AcsDocument)
	# # Set the autocompletion dialog to appear as soon as 1 character is typed
	# editor.setAutoCompletionThreshold(2)
	#
	# """
	# Customization - CALL TIPS (Not usable without a lexer)
	# """
	# # # Set the call tips foreground and background color
	# # calltip_fg_color = QColor("#7f7f0000")
	# # calltip_bg_color = QColor("#7f0000ff")
	# # editor.setCallTipsForegroundColor(calltip_fg_color)
	# # editor.setCallTipsBackgroundColor(calltip_bg_color)
	# # # Set the call tips to appear above the text
	# # editor.setCallTipsPosition(QsciScintilla.CallTipsAboveText)
	# # # Set the call tips to ve displayed without any context
	# # editor.setCallTipsStyle(QsciScintilla.CallTipsNoContext)
	# # # Make the call tips visible
	# # editor.setCallTipsVisible(0)
	editor.setText(initial)
	return editor


