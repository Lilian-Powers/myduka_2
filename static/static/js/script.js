<script>
    let myform = document.getElementById("myform");
    myform.addEventListener("submit", function (e) {
        console.log(e);
        e.preventDefault();
        let basic_salary = parseFloat(document.getElementById("basic_salary").value);
        let total_benefits = parseFloat(document.getElementById("total_benefits").value);
        console.log(basic_salary, total_benefits);

        if (isNaN(basic_salary) || isNaN(total_benefits)) {
            document.getElementById("error").innerText = "Ensure you have filled all the inputs into the spaces provided ";
        } else {
            function grossSalary(basic, benefits) {
                return basic + benefits;
            }
        }

            let gross = grossSalary(basic_salary, total_benefits);

            function Nhif(gross_salary) {
                if (gross_salary <= 5999) {
                    return 150;
                } else if (gross_salary <= 7999) {
                    return 300;
                } else if (gross_salary <= 11999) {
                    return 400;
                } else if (gross_salary <= 14999) {
                    return 500;
                } else if (gross_salary <= 19999) {
                    return 600;
                } else if (gross_salary <= 24999) {
                    return 750;
                } else if (gross_salary <= 29999) {
                    return 850;
                } else if (gross_salary <= 34999) {
                    return 900;
                } else if (gross_salary <= 39999) {
                    return 950;
                } else if (gross_salary <= 44999) {
                    return 1000;
                } else if (gross_salary <= 49999) {
                    return 1100;
                } else if (gross_salary <= 59999) {
                    return 1200;
                } else if (gross_salary <= 69999) {
                    return 1300;
                } else if (gross_salary <= 79999) {
                    return 1400;
                } else if (gross_salary <= 89999) {
                    return 1500;
                } else if (gross_salary <= 99999) {
                    return 1600;
                } else {
                    return 1700;
                }
            }

            let nhif = Nhif(gross);
            console.log("nhif: ", nhif);

            function Nssf(gross_salary) {
                return 0.06 * gross_salary;
            }
            let nssf = Nssf(gross);
            console.log("nssf: ", nssf);

            function Nhdf(gross_salary) {
                return 0.015 * gross_salary;
            }
            let nhdf = Nhdf(gross);
            console.log("nhdf: ", nhdf);

            function taxableIncome(gross_salary, nhif, nhdf, nssf) {
                return gross_salary - nhif - nhdf - nssf;
            }
            let taxable_income = taxableIncome(gross, nhif, nhdf, nssf);
            console.log("taxable_income: ", taxable_income);

            function Payee(taxable_income) {
                let rem = 0;
                let paye = 0;
                if (taxable_income <= 24000) {
                    paye = 0;
                } else if (taxable_income > 24000) {
                    paye = 0.10 * 24000;
                    rem = taxable_income - 24000;
                }
                if (rem > 0) {
                    if (rem > 8333) {
                        paye = paye + (0.25 * 8333);
                        rem = rem - 8333;
                    } else if (rem <= 8333) {
                        paye = paye + (0.25 * rem);
                        rem = 0;
                    }
                }
                if (rem > 0) {
                    if (rem > 467667) {
                        paye = paye + (0.3 * 467667);
                        rem = rem - 467667;
                    } else if (rem <= 467667) {
                        paye = paye + (0.3 * rem);
                        rem = 0;
                    }
                }
                if (rem > 0) {
                    if (rem > 300000) {
                        paye = paye + (0.325 * 300000);
                        rem = rem - 300000;
                    } else if (rem <= 300000) {
                        paye = paye + (0.325 * rem);
                        rem = 0;
                    }
                }

                if (rem > 0) {
                    paye = rem * 0.35;
                }
                return paye;
            }

            let payee = Payee(taxable_income);
            console.log("Payee: ", payee);
            let relief = 2400;

            function netPay(gross, nhif, nssf, nhdf, payee, relief) {
                return gross - nhif - nssf - nhdf - payee + relief;
            }
            let net_pay = netPay(gross, nhif, nssf, nhdf, payee, relief);
            console.log("Net Pay: ", net_pay);

            let table = document.getElementById("table");
            let tbody = document.getElementsByTagName("tbody")[0];
            let newrow = tbody.insertRow();

            newrow.insertCell(0).textContent = gross;
            newrow.insertCell(1).textContent = nhif;
            newrow.insertCell(2).textContent = nhdf;
            newrow.insertCell(3).textContent = nssf;
            newrow.insertCell(4).textContent = payee;
            newrow.insertCell(5).textContent = net_pay;

            myform.reset();
            document.getElementById("error").innerText = "";
        }
    });
</script>
