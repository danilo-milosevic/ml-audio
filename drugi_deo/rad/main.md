---
header-includes: |
  \usepackage{graphicx}
  \usepackage{array}
  \usepackage[a4paper, total={6in, 8in}]{geometry}
  \renewcommand{\contentsname}{Садржај}

  \usepackage{fontspec}
  \usepackage{polyglossia}
  \setdefaultlanguage{serbian}
  \setotherlanguage{english}

  \setmainfont{Times New Roman}
---

{{include sections/0_front/main.md}}

\newpage

\tableofcontents

\newpage

{{include sections/1_introduction/main.md}}

\newpage

{{include sections/2_basics/main.md}}

\newpage

{{include sections/3_emotion_cnn/main.md}}

\newpage

{{include sections/4_emotion_gnn/main.md}}

\newpage

{{include sections/5_conclusion/main.md}}

{{include sections/6_literature/main.md}}