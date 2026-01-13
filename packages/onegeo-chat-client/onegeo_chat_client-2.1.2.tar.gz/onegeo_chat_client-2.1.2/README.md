# Onegeo chat project client


<!-- TABLE OF CONTENTS -->

# 📗 Table of Contents

- [📖 About the Project](#about-project)
- [💻 Getting Started](#getting-started)
- [👥 Authors](#authors)
- [📝 License](#license)


## 📖 [Onegeo Chat] <a name="about-project"></a>

Onegeo Chat is a RAG based chatbot.

It can harvest data from several sources.


## 💻 Getting Started <a name="getting-started"></a>

### Create and Publish OGC remote with Test PyPI

To create a version of the **onegeo-chat-client**, simply update the project **version** in the *pyproject.toml* file with <current_version>.

First, **create** the **package** with the following command:
```bash
cd onegeo_chat_client
python -m build
```
Then, **publish** it on **Test PyPI** with this command:
```bash
twine upload dist/*
```
You will need a Test PyPI account.
Take note that package file name can't be reused (desired behavior from Test PyPI).

### Install and Use OGC

Then, you can **install** the **client** with this command:
```bash
pip install onegeo-chat-client==<current_version>
```

As for the use, you can simply add this line to your files :
```py
from onegeo_chat_client import import Data, OnegeoChatClient
```
to use the classe defined in the client.

## 👥 Authors <a name="authors"></a>

👤 **Mathilde POMMIER**

- Mail: mpommier@neogeo.fr

👤 **Sébastien DA ROCHA**

- Mail: sdarocha@neogeo.fr

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## 📝 License <a name="license"></a>

This project is [AGPL 3.0](../LICENSE) licensed.

<p align="right">(<a href="#readme-top">back to top</a>)</p>