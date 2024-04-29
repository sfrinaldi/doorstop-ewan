# SPDX-License-Identifier: LGPL-3.0-only

"""Unit tests for the doorstop.core.publishers.latex module."""

# pylint: disable=unused-argument,protected-access

import unittest

from doorstop.common import DoorstopError
from doorstop.core import publisher
from doorstop.core.publishers.tests.helpers import getLines
from doorstop.core.tests import MockDataMixIn, MockItemAndVCS


class TestPublisherModuleEnvironments(MockDataMixIn, unittest.TestCase):
    """Unit tests for _environments_ in the doorstop.core.publishers.latex module."""

    def test_multiline_math(self):
        """Verify that math environments over multiple lines are published correctly."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of multiline math environments." + "\n"
            r"  " + "\n"
            r"  $$" + "\n"
            r"  \frac{a*b}{0} = \infty{}" + "\n"
            r"  \text{where}" + "\n"
            r"  a = 2.0" + "\n"
            r"  b = 32" + "\n"
            r"  $$"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of multiline math environments.\\" + "\n\n"
            r"$\\" + "\n"
            r"\frac{a*b}{0} = \infty{}\\" + "\n"
            r"\text{where}\\" + "\n"
            r"a = 2.0\\" + "\n"
            r"b = 32\\" + "\n"
            r"$" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_multiline_math_error(self):
        """Verify that math environments that are badly specified generates an error."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of multiline math environments." + "\n"
            r"  " + "\n"
            r"  $$\frac{a*b}{0} = \infty{}$$where$$s" + "\n"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        # Act & Assert
        with self.assertRaises(DoorstopError):
            _ = getLines(publisher.publish_lines(item, ".tex"))

    def test_enumerate_environment_normal_ending(self):
        """Verify that enumerate environments are published correctly with normal ending."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of enumeration end." + "\n"
            r"  " + "\n"
            r"  1. item one" + "\n"
            r"  21. item two" + "\n"
            r"  441. item three"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of enumeration end.\\" + "\n\n"
            r"\begin{enumerateDeep}" + "\n"
            r"\item item one" + "\n"
            r"\item item two" + "\n"
            r"\item item three" + "\n"
            r"\end{enumerateDeep}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_enumerate_environment_empty_row_ending(self):
        """Verify that enumerate environments are published correctly with and empty row ending."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of enumeration end." + "\n"
            r"  " + "\n"
            r"  1. item one" + "\n"
            r"  21. item two" + "\n"
            r"  441. item three" + "\n"
            r"" + "\n"
            r"  This is not an item!"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of enumeration end.\\" + "\n\n"
            r"\begin{enumerateDeep}" + "\n"
            r"\item item one" + "\n"
            r"\item item two" + "\n"
            r"\item item three" + "\n"
            r"\end{enumerateDeep}" + "\n\n"
            r"This is not an item!" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_enumerate_environment_multiline_item(self):
        """Verify that enumerate environments are published correctly with multiline items."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of enumeration end." + "\n"
            r"  " + "\n"
            r"  1. item one" + "\n"
            r"  21. item two" + "\n"
            r"  441. item three" + "\n"
            r"  This still a part of the previous item!" + "\n"
            r"  **This too!**" + "\n"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of enumeration end.\\" + "\n\n"
            r"\begin{enumerateDeep}" + "\n"
            r"\item item one" + "\n"
            r"\item item two" + "\n"
            r"\item item three" + "\n"
            r"This still a part of the previous item!" + "\n"
            r"\textbf{This too!}" + "\n"
            r"\end{enumerateDeep}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_itemize_environment_normal_ending(self):
        """Verify that itemize environments are published correctly with normal ending."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of itemization end." + "\n"
            r"  " + "\n"
            r"  * item one" + "\n"
            r"  + item two" + "\n"
            r"  - item three"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of itemization end.\\" + "\n\n"
            r"\begin{itemizeDeep}" + "\n"
            r"\item item one" + "\n"
            r"\item item two" + "\n"
            r"\item item three" + "\n"
            r"\end{itemizeDeep}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_itemize_environment_empty_row_ending(self):
        """Verify that itemize environments are published correctly with and empty row ending."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of itemization end." + "\n"
            r"  " + "\n"
            r"  * item one" + "\n"
            r"  + item two" + "\n"
            r"  - item three" + "\n"
            r"" + "\n"
            r"  This is not an item!"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of itemization end.\\" + "\n\n"
            r"\begin{itemizeDeep}" + "\n"
            r"\item item one" + "\n"
            r"\item item two" + "\n"
            r"\item item three" + "\n"
            r"\end{itemizeDeep}" + "\n\n"
            r"This is not an item!" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_itemize_environment_multiline_item(self):
        """Verify that itemize environments are published correctly with multiline items."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of itemization end." + "\n"
            r"  " + "\n"
            r"  * item one" + "\n"
            r"  + item two" + "\n"
            r"  - item three" + "\n"
            r"  This still a part of the previous item!" + "\n"
            r"  This too!" + "\n"
            r"  " + "\n"
            r"  But not this!" + "\n"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of itemization end.\\" + "\n\n"
            r"\begin{itemizeDeep}" + "\n"
            r"\item item one" + "\n"
            r"\item item two" + "\n"
            r"\item item three" + "\n"
            r"This still a part of the previous item!" + "\n"
            r"This too!" + "\n"
            r"\end{itemizeDeep}" + "\n\n"
            r"But not this!" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_table_no_start_at_eof(self):
        """Verify that a table is not started if end-of-file is reached."""
        # Setup
        generated_data = (
            r"text: |" + "\n" r"  Test of table." + "\n" r"  " + "\n" r"  |||"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of table.\\" + "\n\n"
            r"|||" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_table_no_start_unbalanced(self):
        """Verify that a table is not started if columns are unbalanced."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of table." + "\n"
            r"  " + "\n"
            r"  |||" + "\n"
            r"  |---|"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of table.\\" + "\n\n"
            r"|||" + "\n"
            r"|---|" + "\n\n"
        )
        # Act
        result = ""
        with self.assertLogs(
            "doorstop.core.publishers._latex_functions", level="WARNING"
        ) as logs:
            result = getLines(publisher.publish_lines(item, ".tex"))
            self.assertIn(
                "WARNING:doorstop.core.publishers._latex_functions:Possibly unbalanced table found.",
                logs.output,
            )
        # Assert
        self.assertEqual(expected, result)

    def test_table_no_start_wrong_dashes(self):
        """Verify that a table is not started if dash count is less than three."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of table." + "\n"
            r"  " + "\n"
            r"  |||" + "\n"
            r"  |-|-|"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of table.\\" + "\n\n"
            r"|||" + "\n"
            r"|-|-|" + "\n\n"
        )
        # Act
        result = ""
        with self.assertLogs(
            "doorstop.core.publishers._latex_functions", level="WARNING"
        ) as logs:
            result = getLines(publisher.publish_lines(item, ".tex"))
            self.assertIn(
                "WARNING:doorstop.core.publishers._latex_functions:Possibly incorrectly specified table found.",
                logs.output,
            )
        # Assert
        self.assertEqual(expected, result)

    def test_plantuml_with_title(self):
        """Verify that a plantuml image is generated correctly with title."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r'  plantuml format="png" alt="State Diagram Loading" title="State Diagram"'
            + "\n"
            r"  @startuml" + "\n"
            r"  scale 600 width" + "\n"
            r"" + "\n"
            r"  [*] -> State1" + "\n"
            r"  State1 --> State2 : Succeeded" + "\n"
            r"" + "\n"
            r"  @enduml" + "\n"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"\hyperref[fig:plant1]{State Diagram}" + "\n"
            r"\begin{plantuml}{State-Diagram}" + "\n"
            r"@startuml" + "\n"
            r"scale 600 width" + "\n\n"
            r"[*] -> State1" + "\n"
            r"State1 --> State2 : Succeeded" + "\n\n"
            r"@enduml" + "\n"
            r"\end{plantuml}" + "\n"
            r"\process{State-Diagram}{0.8\textwidth}{State Diagram}{1}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_plantuml_no_title(self):
        """Verify that an error is raised if a plantUML is missing the title."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r'  plantuml format="png"' + "\n"
            r"  @startuml" + "\n"
            r"  scale 600 width" + "\n"
            r"" + "\n"
            r"  [*] -> State1" + "\n"
            r"  State1 --> State2 : Succeeded" + "\n"
            r"" + "\n"
            r"  @enduml" + "\n"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        # Act & Assert
        with self.assertRaises(DoorstopError):
            _ = getLines(publisher.publish_lines(item, ".tex"))

    def test_missing_ending_code(self):
        """Verify that the code block ended correctly even if ending was not detected before end-of-file."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of code block." + "\n\n"
            r"  ```" + "\n"
            r"  This is an unended code block."
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of code block.\\" + "\n\n"
            r"\begin{lstlisting}" + "\n"
            r"This is an unended code block." + "\n"
            r"\end{lstlisting}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_immediate_code_block(self):
        """Verify that if the code block starts immediately, it is still published correctly."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  ```python" + "\n"
            r"  def fibonacci(n):" + "\n"
            r"      a, b = 0, 1" + "\n"
            r"      while a < n:" + "\n"
            r"          print(a, end=' ')" + "\n"
            r"          a, b = b, a+b" + "\n"
            r"      print()" + "\n"
            r"  fibonacci(1000)" + "\n"
            r"  ```"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"\begin{lstlisting}[language=python]" + "\n"
            r"def fibonacci(n):" + "\n"
            r"    a, b = 0, 1" + "\n"
            r"    while a < n:" + "\n"
            r"        print(a, end=' ')" + "\n"
            r"        a, b = b, a+b" + "\n"
            r"    print()" + "\n"
            r"fibonacci(1000)" + "\n"
            r"\end{lstlisting}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_missing_ending_plantuml(self):
        """Verify that the plantUML block ended correctly even if ending was not detected before end-of-file."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of plantUML block." + "\n\n"
            r'  plantuml format="png" alt="State Diagram Loading" title="State Diagram"'
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of plantUML block.\\" + "\n\n"
            r"\hyperref[fig:plant1]{State Diagram}" + "\n"
            r"\begin{plantuml}{State-Diagram}" + "\n"
            r"\end{plantuml}" + "\n"
            r"\process{State-Diagram}{0.8\textwidth}{State Diagram}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_missing_ending_table(self):
        """Verify that the table ended correctly even if ending was not detected before end-of-file."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  Test of table ending." + "\n\n"
            r"  |cool|table|" + "\n"
            r"  |---|---|" + "\n"
            r"  |without|end|"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"Test of table ending.\\" + "\n\n"
            r"\begin{longtable}{|l|l|}" + "\n"
            r"cool&table\\" + "\n"
            r"\hline" + "\n"
            r"without&end\\" + "\n"
            r"\end{longtable}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_missing_ending_newline_for_list(self):
        """Verify that a list is ended correctly even if ending was not detected before end-of-file."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  List without newline:" + "\n"
            r"  1. Item 1" + "\n"
            r"    1. Item 1.1"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        expected = (
            r"\section{REQ-001}\label{REQ-001}\zlabel{REQ-001}" + "\n\n"
            r"List without newline:" + "\n"
            r"\begin{enumerateDeep}" + "\n"
            r"\item Item 1" + "\n"
            r"\begin{enumerateDeep}" + "\n"
            r"\item Item 1.1" + "\n"
            r"\end{enumerateDeep}" + "\n"
            r"\end{enumerateDeep}" + "\n\n"
        )
        # Act
        result = getLines(publisher.publish_lines(item, ".tex"))
        # Assert
        self.assertEqual(expected, result)

    def test_missing_changing_list_indentation(self):
        """Verify that a list throws an error if indentation is changed in the middle of the list."""
        # Setup
        generated_data = (
            r"text: |" + "\n"
            r"  List without newline:" + "\n"
            r"    1. Item 1" + "\n"
            r"        1. Item 1.1"
        )
        item = MockItemAndVCS(
            "path/to/REQ-001.yml",
            _file=generated_data,
        )
        # Act & Assert
        with self.assertRaises(DoorstopError):
            _ = getLines(publisher.publish_lines(item, ".tex"))
