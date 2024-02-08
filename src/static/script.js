const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");


const BOT_IMG = "https://png.pngtree.com/png-vector/20221230/ourmid/pngtree-catfish-logo-png-image_6543347.png";
const PERSON_IMG = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTj7dS65P6kTaMDBRyvU0X2XIBIK3j8iiiB6Q&usqp=CAU";
const BOT_NAME = "ChatFish";

const MD = window.markdownit();


msgerForm.addEventListener("submit", event => {
  event.preventDefault();

  const msgText = msgerInput.value;
  if (!msgText) return;
  appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
  appendThinkingMessage();
  msgerChat.scrollTop = msgerChat.scrollHeight;

  socket.send(msgText);

  msgerInput.value = "";
});

socket.on('message', function(text) {
    removeThinkingMessage();
    appendMessage(BOT_NAME, BOT_IMG, "left", text);
    msgerChat.scrollTop = msgerChat.scrollHeight;
});

function appendThinkingMessage() {
  const thinkingMessage = `
    <div class="msg thinking-msg">
      <div class="msg-bubble">
        <div class="msg-text">Thinking...</div>
      </div>
    </div>
  `;
  msgerChat.insertAdjacentHTML("beforeend", thinkingMessage);
}

function removeThinkingMessage() {
  const thinkingMsgElement = document.querySelector('.thinking-msg');
  if (thinkingMsgElement) {
    thinkingMsgElement.remove();
  }
}

function appendMessage(name, img, side, text) {
  const isBotMessage = side === "left";

  msgerChat.scrollTop = msgerChat.scrollHeight;

  const parsedText = parseMarkdownAndCodeBlocks(text);

  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${parsedText}</div>
      </div>
    </div>
  `;

  if (isBotMessage) {
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop = msgerChat.scrollHeight;
  } else {
    // If it's not a bot message, directly insert the message
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop = msgerChat.scrollHeight;
  }
}

function parseMarkdownAndCodeBlocks(text) {
  const md = window.markdownit({
    html: true,
    breaks: true,
    langPrefix: 'hljs language-',
    highlight: function (str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return '<pre class="hljs"><code>' + hljs.highlight(lang, str, true).value + '</code></pre>';
        } catch (__) {}
      }
      return '';
    }
  });
  const renderedText = md.render(text);
  const trimmedText = renderedText.trim();

  return trimmedText;
}

function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}
