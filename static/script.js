const messageForm = document.querySelector(".message-form");
const messageBoard = document.querySelector(".message-board");

const createMessage = async () => {
  const messageText = document.querySelector(".message-text").value;
  const messageImage = document.querySelector(".message-image").files[0];
  const formData = new FormData();

  formData.append("text", messageText);
  formData.append("image", messageImage);

  try {
    const response = await fetch("/api/message", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      alert("系統無回應，請重試。");
      throw new Error("系統無回應");
    }
    const result = await response.json();
    if (result.status !== "ok") {
      alert("留言發佈失敗，請重試。");
      throw new Error("留言發佈失敗");
    }
    messageForm.reset();
    loadMessages();
  } catch (error) {
    console.error(error);
    alert("發生意外錯誤，請稍後再試");
  }
};

const loadMessages = async () => {
  try {
    const response = await fetch("/api/messages", {
      method: "GET",
    });
    const result = await response.json();
    if (!response.ok || result.status !== "ok") {
      messageBoard.textContent = "留言取得失敗，請重試。";
      throw new Error("留言取得失敗");
    }
    messageBoard.innerHTML = "";
    if (result.data !== null && result.data.length > 0) {
      messageBoard.classList.add("open");
      result.data.forEach((message) => {
        displayMessages(message);
      });
    }
  } catch (error) {
    messageBoard.textContent = "發生意外錯誤，請重試。";
    console.error(error);
  }
};

const displayMessages = (message) => {
  const text = message.text;
  const imageUrl = message.imageUrl;
  messageBoard.classList.add("open");
  const messageCard = document.createElement("div");
  messageCard.className = "message-card";
  const imageContainer = document.createElement("div");
  imageContainer.className = "message-card-image-container";
  const cardImage = document.createElement("img");
  cardImage.className = "message-card-image";
  cardImage.src = imageUrl;
  const cardContent = document.createElement("div");
  cardContent.className = "message-card-content";
  const p = document.createElement("p");
  p.textContent = text;
  messageCard.appendChild(imageContainer);
  imageContainer.appendChild(cardImage);
  messageCard.appendChild(cardContent);
  cardContent.appendChild(p);
  messageBoard.appendChild(messageCard);
};

messageForm.addEventListener("submit", (e) => {
  e.preventDefault();
  createMessage();
});
loadMessages();
