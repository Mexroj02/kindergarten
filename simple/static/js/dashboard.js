document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".dashboard-card");

  cards.forEach(card => {
    card.addEventListener("click", () => {
      alert(`Navigating to ${card.dataset.title}`);
      // Implement real navigation if needed
    });
  });
});
