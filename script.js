 function showMessage() {
  document.getElementById("message").innerHTML =
    "Thanks for your interest, let's talk.";
  document.getElementById("hireBtn").style.backgroundColor = "#4ecca3";
  document.getElementById("hireBtn").style.color = "#1a1a2e";
}
/// Skill tag stagger animation
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.skill-tag').forEach((tag, index) => {
    tag.style.animationDelay = `${0.6 + index * 0.08}s`;
  });
});