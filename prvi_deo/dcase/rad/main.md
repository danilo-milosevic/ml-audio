---
header-includes: |
  \usepackage{graphicx}
  \usepackage{array}
  \usepackage[a4paper, total={6in, 8in}]{geometry}
  \renewcommand{\contentsname}{Sadržaj}

  \usepackage{fontspec}
  \usepackage{polyglossia}
  \setdefaultlanguage[script=Latin]{serbian}

  \setmainfont{Times New Roman}
---

{{include sections/0_front/main.md}}

\newpage

\tableofcontents

\newpage

{{include sections/1_problem/main.md}}

{{include sections/2_architecture/main.md}}

\newpage

{{include sections/3_improvements/main.md}}
