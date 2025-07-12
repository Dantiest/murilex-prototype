const profits = document.querySelectorAll('.available.profit');
const balances = document.querySelectorAll('.price-value.balance'); // Use the correct selector

profits.forEach((profit, index) => {
    const balance = parseFloat(balances[index].textContent); // Convert text content to a number
    profit.textContent = `${(balance - 1000) / 10}%`;
});