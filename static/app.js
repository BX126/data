const searchInput = document.querySelector("#searchInput");
const clearSearch = document.querySelector("#clearSearch");
const cards = Array.from(document.querySelectorAll(".scene-card"));
const emptyState = document.querySelector("#emptyState");
const modalOverlay = document.querySelector("#modalOverlay");
const modalClose = document.querySelector("#modalClose");
const modalContents = Array.from(document.querySelectorAll(".modal-content"));

function normalized(value) {
  return value.trim().toLowerCase();
}

function applyFilters() {
  const terms = normalized(searchInput.value).split(/\s+/).filter(Boolean);
  let visibleCount = 0;

  cards.forEach((card) => {
    const searchText = card.dataset.search || "";
    const matchesSearch = terms.every((term) => searchText.includes(term));

    card.hidden = !matchesSearch;
    if (matchesSearch) visibleCount += 1;
  });

  emptyState.hidden = visibleCount > 0;
}

function openModal(sceneId) {
  modalContents.forEach((content) => {
    content.hidden = content.dataset.modalId !== sceneId;
  });
  modalOverlay.hidden = false;
  document.body.classList.add("is-modal-open");
  modalClose.focus();
}

function closeModal() {
  modalOverlay.hidden = true;
  document.body.classList.remove("is-modal-open");
}

cards.forEach((card) => {
  card.addEventListener("click", () => openModal(card.dataset.sceneId));
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openModal(card.dataset.sceneId);
    }
  });
});

document.addEventListener("click", (event) => {
  const similarButton = event.target.closest("[data-open-scene]");
  if (similarButton) {
    openModal(similarButton.dataset.openScene);
  }
});

searchInput.addEventListener("input", applyFilters);

clearSearch.addEventListener("click", () => {
  searchInput.value = "";
  searchInput.focus();
  applyFilters();
});

modalClose.addEventListener("click", closeModal);

modalOverlay.addEventListener("click", (event) => {
  if (event.target === modalOverlay) {
    closeModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modalOverlay.hidden) {
    closeModal();
  }
});

applyFilters();
