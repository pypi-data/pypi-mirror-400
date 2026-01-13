moodswing
=======================================================================================================
|pypi| |pypi_downloads| |tests|

Track changes in sentiment over the course of a narrative text. Inspired by Matthew Jockers' **syuzhet** R package, **moodswing** brings sentiment trajectory analysis to Python with both dictionary-based and neural approaches.

**moodswing** helps you:

- 📊 **Visualize emotional arcs** in novels, memoirs, and other narratives
- 📚 **Use proven lexicons** (Syuzhet, AFINN, Bing, NRC) optimized for different text types
- 🧠 **Leverage spaCy models** for context-aware sentiment analysis
- 🔬 **Apply DCT smoothing** to reveal underlying narrative structure
- 🎨 **Create publication-ready plots** with flexible visualization options

Based on research in computational literary analysis, this package makes it easy to uncover the emotional patterns that shape stories.


Quick Start
-----------

Install from PyPI:

.. code-block:: bash

    pip install moodswing

For spaCy support (optional):

.. code-block:: bash

    pip install moodswing
    python -m spacy download en_core_web_sm


Example: Analyze a Novel
-------------------------

.. code-block:: python

    from moodswing import (
        DictionarySentimentAnalyzer,
        Sentencizer,
        DCTTransform,
        prepare_trajectory,
        plot_trajectory,
    )
    from moodswing.data import load_sample_text

    # Load a sample novel
    doc_id, text = load_sample_text("madame_bovary")

    # Split into sentences
    sentences = Sentencizer().split(text)

    # Score each sentence
    analyzer = DictionarySentimentAnalyzer()
    scores = analyzer.sentence_scores(sentences, method="syuzhet")

    # Create smoothed trajectory
    trajectory = prepare_trajectory(
        scores,
        rolling_window=int(len(scores) * 0.1),
        dct_transform=DCTTransform(low_pass_size=10, output_length=200, scale_range=True)
    )

    # Plot the emotional arc
    plot_trajectory(trajectory, title="Madame Bovary: Sentiment Trajectory")


Features
--------

**Four Sentiment Lexicons**
  - **Syuzhet**: Optimized for narrative analysis
  - **AFINN**: Includes slang and informal language
  - **Bing**: Binary positive/negative classification
  - **NRC**: Multi-dimensional emotions (joy, fear, anger, etc.) with multilingual support

**Two Analysis Approaches**
  - **Dictionary-based**: Fast, transparent word lookup
  - **spaCy-based**: Context-aware neural models (handles negation, sarcasm)

**Advanced Smoothing**
  - **Rolling mean**: Local trend smoothing
  - **DCT (Discrete Cosine Transform)**: Reveals overall narrative shape
  - Compatible with R's syuzhet package for reproducible research

**Flexible Visualization**
  - Built-in plotting with customizable colors and components
  - Export to pandas DataFrame for seaborn, plotly, or custom plots
  - Publication-ready output with figure size/DPI control


Documentation
-------------

Full documentation with tutorials, examples, and API reference:

📖 **https://browndw.github.io/moodswing/**

- `Get Started <https://browndw.github.io/moodswing/get-started.html>`_: Complete walkthrough with scholarly background
- `Using Sentiment Lexicons <https://browndw.github.io/moodswing/sentiment-lexicons.html>`_: Compare and choose the right dictionary
- `Using spaCy <https://browndw.github.io/moodswing/sentiment-spacy.html>`_: Context-aware analysis with neural models
- `Visualization Guide <https://browndw.github.io/moodswing/visualization-guide.html>`_: Custom plotting and styling
- `Examples Gallery <https://browndw.github.io/moodswing/examples-gallery.html>`_: Ready-to-use code for common tasks
- `Technical Notes <https://browndw.github.io/moodswing/technical-notes.html>`_: DCT mathematics and R compatibility
- `API Reference <https://browndw.github.io/moodswing/reference/>`_: Complete function documentation


Citation
--------

If you use this package in your research, please cite:

.. code-block:: bibtex

    @software{moodswing2025,
      author = {Brown, David},
      title = {moodswing: Sentiment Trajectory Analysis for Python},
      year = {2025},
      url = {https://github.com/browndw/moodswing}
    }

This package is based on Matthew Jockers' **syuzhet** R package:

.. code-block:: bibtex

    @article{jockers2015syuzhet,
      title={Revealing sentiment and plot arcs with the Syuzhet package},
      author={Jockers, Matthew L},
      year={2015}
    }


License
-------

Code licensed under `MIT License <https://opensource.org/licenses/MIT>`_.

See `LICENSE <https://github.com/browndw/moodswing/blob/main/LICENSE>`_ file.

.. |pypi| image:: https://badge.fury.io/py/moodswing.svg
    :target: https://badge.fury.io/py/moodswing
    :alt: PyPI Version

.. |pypi_downloads| image:: https://img.shields.io/pypi/dm/moodswing
    :target: https://pypi.org/project/moodswing/
    :alt: Downloads from PyPI

.. |tests| image:: https://github.com/browndw/moodswing/actions/workflows/test.yml/badge.svg
    :target: https://github.com/browndw/moodswing/actions/workflows/test.yml
    :alt: Test Status
