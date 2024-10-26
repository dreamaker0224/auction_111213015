let next = document.querySelector(".next");
let prev = document.querySelector(".prev");
console.log(1)
next.addEventListener("click", function () {
  let items = document.querySelectorAll(".slide-item");
  document.querySelector(".slide").appendChild(items[0]);
});

prev.addEventListener("click", function () {
  let items = document.querySelectorAll(".slide-item");
  document.querySelector(".slide").prepend(items[items.length - 1]);
});
