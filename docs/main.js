
addEventListener('scroll', () => {
    console.log("scrolling");
});

const BOTTOM_THRESHOLD = 100;
function getIsBottom() {
  return window.innerHeight + window.scrollY + BOTTOM_THRESHOLD >= document.body.offsetHeight;
}