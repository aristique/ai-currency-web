const $ = id => document.getElementById(id);
let snapshot = null;
let loading = false;
const current = new Date();
$("date").value = [current.getFullYear(), String(current.getMonth()+1).padStart(2,"0"), String(current.getDate()).padStart(2,"0")].join("-");
function validate() {
  const raw = $("amount").value.trim().replace(",", ".");
  const amount = Number(raw);
  const valid = raw !== "" && Number.isFinite(amount) && amount > 0 && amount <= 1e15;
  $("convert").disabled = !valid || !snapshot || loading || !$("from").value || !$("to").value;
  $("validation").textContent = valid ? "" : "Введите число больше нуля и не более 10¹⁵.";
  $("amount-unit").textContent = $("from").value || "";
}
function clearResult() { $("result").textContent = "—"; $("equation").textContent = "Укажите сумму и нажмите «Конвертировать»"; }
async function loadRates(cached=false) {
  loading = true; snapshot = null; clearResult(); validate();
  $("refresh").disabled = true; $("cached").hidden = true;
  $("notice-title").textContent = "Получаем официальные данные";
  $("status").textContent = "Подождите несколько секунд…";
  try {
    const response = await fetch(cached ? "/api/rates?cached=1" : "/api/rates?date="+encodeURIComponent($("date").value));
    const data = await response.json();
    if (!response.ok) {
      $("cached").hidden = !data.cacheAvailable;
      $("cached").textContent = "Использовать курс от " + (data.cachedDate || "");
      throw new Error(data.error);
    }
    const oldFrom = $("from").value || "EUR", oldTo = $("to").value || "MDL";
    for (const id of ["from","to"]) {
      $(id).replaceChildren(...Object.keys(data.rates).map(code => {
        const option = document.createElement("option"); option.value=code; option.textContent=code; return option;
      }));
    }
    $("from").value = oldFrom in data.rates ? oldFrom : Object.keys(data.rates)[0];
    $("to").value = oldTo in data.rates ? oldTo : "MDL";
    snapshot = data.snapshot;
    $("rate-date").textContent = data.date;
    $("mode").textContent = data.cached ? "Сохранённый курс" : "Курс получен";
    $("notice-title").textContent = data.cached ? "Работа с сохранёнными данными" : "Курс готов к расчёту";
    $("status").textContent = data.warning || "Официальный курс на " + data.date + ". Данные сохранены для работы без интернета.";
  } catch(error) {
    $("mode").textContent = "Курс недоступен";
    $("rate-date").textContent = "—";
    $("notice-title").textContent = "Не удалось обновить курс";
    $("status").textContent = error.message || "Проверьте соединение с приложением.";
  } finally { loading=false; $("refresh").disabled=false; validate(); }
}
$("converter").addEventListener("submit", async event => {
  event.preventDefault(); validate(); if ($("convert").disabled) return;
  $("convert").disabled=true;
  try {
    const response=await fetch("/api/convert",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({snapshot,amount:$("amount").value,from:$("from").value,to:$("to").value})});
    const data=await response.json(); if (!response.ok) throw new Error(data.error);
    $("result").textContent = new Intl.NumberFormat("ru-RU",{minimumFractionDigits:2,maximumFractionDigits:2}).format(Number(data.amount))+" "+data.to;
    $("equation").textContent = $("amount").value+" "+data.from+" → "+data.to;
    $("validation").textContent="";
  } catch(error) { $("validation").textContent=error.message; }
  finally { validate(); }
});
for (const id of ["amount","from","to"]) $(id).addEventListener("input",()=>{clearResult();validate();});
$("swap").addEventListener("click",()=>{const from=$("from").value;$("from").value=$("to").value;$("to").value=from;clearResult();validate();});
$("refresh").addEventListener("click",()=>loadRates(false));
$("cached").addEventListener("click",()=>loadRates(true));
$("date").addEventListener("change",()=>loadRates(false));
loadRates();
