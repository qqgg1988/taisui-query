// 加载太岁数据
let taishiData = [];
fetch('output.json')
    .then(response => response.json())
    .then(data => {
        taishiData = data;
        initializeYearOptions();
    })
    .catch(error => console.error('Error loading data:', error));

// 初始化年份选项
function initializeYearOptions() {
    const yearSelect = document.getElementById('year');
    
    // 添加1924-2043年的选项
    for (let year = 1924; year <= 2043; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        yearSelect.appendChild(option);
    }
}

// 显示输入部分
function showInputSection() {
    document.getElementById('inputSection').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
}

// 显示结果部分
function showResultSection() {
    document.getElementById('inputSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'block';
}

// 获取实际查询年份（考虑立春前后）
function getActualYear(inputYear, isBeforeLichun) {
    // 特殊处理1924年立春前的情况
    if (inputYear === 1924 && isBeforeLichun) {
        return 1983;
    }
    // 其他情况按正常逻辑处理
    return isBeforeLichun ? inputYear - 1 : inputYear;
}

// 查找匹配的太岁数据
function findMatchingTaishi(year) {
    return taishiData.find(item => {
        const years = item.Year.split('、').map(y => parseInt(y.trim()));
        return years.includes(parseInt(year));
    });
}

// 初始化事件监听
document.addEventListener('DOMContentLoaded', function() {
    // 提交按钮点击事件
    document.getElementById('submitBtn').addEventListener('click', function() {
        const year = document.getElementById('year').value;
        if (!year) {
            alert('请选择出生年份！');
            return;
        }

        // 获取立春前后选项
        const isBeforeLichun = document.querySelector('input[name="lichun"]:checked').value === 'before';
        
        // 计算实际查询年份
        const actualYear = getActualYear(parseInt(year), isBeforeLichun);
        
        const matchingTaishi = findMatchingTaishi(actualYear);
        if (matchingTaishi) {
            // 更新结果页面
            document.getElementById('resultImage').src = matchingTaishi.Poster.tmp_download_url;
            let yearDisplay = year;
            // 特殊处理1924年立春前的显示
            if (year === 1924 && isBeforeLichun) {
                yearDisplay = '1924（特殊年份）';
            }
            document.getElementById('yearInfo').textContent = 
                `${yearDisplay}年${isBeforeLichun ? '（立春前）' : '（立春后）'} - ${matchingTaishi.Animal}年`;
            document.getElementById('additionalInfo').textContent = 
                `太岁：${matchingTaishi.Taishui} | 纳音：${matchingTaishi.Nayin} | 干支：${matchingTaishi.Ganzhi}`;
            showResultSection();
        } else {
            alert('未找到对应年份的太岁信息！');
        }
    });
}); 