for (const marquee of document.querySelectorAll(".marquee > *")) {
    const rect = marquee.getBoundingClientRect();
    marquee.style.animationDuration = (rect.width / 100) + "s";
}
