// ===============================================
// COLLISION RESISTANCE TEST - ENHANCED VERSION
// ===============================================

let currentScenario = 'custom';

function setCollisionScenario(scenario) {
    currentScenario = scenario;
    
    // Update button styles
    ['custom', 'password', 'typo', 'transaction'].forEach(s => {
        const btn = document.getElementById(`btn-${s}`);
        if (btn) {
            if (s === scenario) {
                btn.className = 'btn btn-primary';
            } else {
                btn.className = 'btn btn-outline';
            }
        }
    });
    
    const customForm = document.getElementById('customInputForm');
    const scenarioDesc = document.getElementById('scenarioDesc');
    const input1 = document.getElementById('input1');
    const input2 = document.getElementById('input2');
    
    if (scenario === 'custom') {
        customForm.style.display = 'block';
        scenarioDesc.style.display = 'none';
        input1.value = 'Hello World';
        input2.value = 'Hello World!';
    } else {
        customForm.style.display = 'block';
        scenarioDesc.style.display = 'block';
        
        switch(scenario) {
            case 'password':
                input1.value = 'MyPassword123';
                input2.value = 'MyPassword124';
                scenarioDesc.innerHTML = `
                    <h4 style="color: var(--primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-key"></i> Password Security Test
                    </h4>
                    <p>Demo: 2 passwords chỉ khác 1 ký tự sẽ có hash hoàn toàn khác nhau.</p>
                    <p style="margin-top: 0.5rem; color: var(--gray); font-size: 0.9rem;">
                        <strong>Ứng dụng:</strong> Trong database, passwords tương tự không thể đoán được từ hash.
                        Attacker không thể brute force từ passwords tương tự.
                    </p>
                `;
                break;
            case 'typo':
                input1.value = 'alice@email.com';
                input2.value = 'ailce@email.com';  // Typo: swapped 'l' and 'i'
                scenarioDesc.innerHTML = `
                    <h4 style="color: var(--primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-spell-check"></i> Typo Detection Test
                    </h4>
                    <p>Demo: Email với typo (hoán đổi 2 chữ cái) sẽ tạo hash hoàn toàn khác.</p>
                    <p style="margin-top: 0.5rem; color: var(--gray); font-size: 0.9rem;">
                        <strong>Ứng dụng:</strong> Data integrity checks - phát hiện ngay cả lỗi nhỏ nhất.
                        File checksums sẽ khác nếu có 1 byte bị corrupt.
                    </p>
                `;
                break;
            case 'transaction':
                input1.value = 'Alice sends 100 BTC to Bob';
                input2.value = 'Alice sends 101 BTC to Bob';
                scenarioDesc.innerHTML = `
                    <h4 style="color: var(--primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-money-bill"></i> Transaction Security Test
                    </h4>
                    <p>Demo: Transactions chỉ khác 1 số sẽ có hash hoàn toàn khác.</p>
                    <p style="margin-top: 0.5rem; color: var(--gray); font-size: 0.9rem;">
                        <strong>Ứng dụng:</strong> Trong blockchain, không thể thay đổi số tiền mà không bị phát hiện.
                        Mỗi transaction có unique hash làm identifier.
                    </p>
                `;
                break;
        }
    }
}

async function runCollisionTest() {
    const loadingEl = document.getElementById('collisionLoading');
    const resultsEl = document.getElementById('collisionResults');
    const input1 = document.getElementById('input1').value.trim();
    const input2 = document.getElementById('input2').value.trim();
    
    if (!input1 || !input2) {
        alert('Vui lòng nhập cả 2 inputs!');
        return;
    }
    
    if (input1 === input2) {
        alert('2 inputs giống nhau! Hãy thay đổi ít nhất 1 ký tự để thấy Avalanche Effect.');
        return;
    }
    
    loadingEl.style.display = 'block';
    resultsEl.style.display = 'none';

    try {
        const response = await fetch(`/test-collision?input1=${encodeURIComponent(input1)}&input2=${encodeURIComponent(input2)}`);
        const data = await response.json();

        if (data.success) {
            displayCollisionResults(data);
        } else {
            alert('Lỗi: ' + data.error);
        }
    } catch (error) {
        alert('Lỗi: ' + error.message);
    } finally {
        loadingEl.style.display = 'none';
        resultsEl.style.display = 'block';
    }
}

function calculateStringSimilarity(str1, str2) {
    const maxLen = Math.max(str1.length, str2.length);
    let matches = 0;
    for (let i = 0; i < Math.min(str1.length, str2.length); i++) {
        if (str1[i] === str2[i]) matches++;
    }
    return ((matches / maxLen) * 100).toFixed(1);
}

function highlightDifferences(str1, str2) {
    const maxLen = Math.max(str1.length, str2.length);
    let html1 = '', html2 = '';
    
    for (let i = 0; i < maxLen; i++) {
        const char1 = i < str1.length ? str1[i] : '';
        const char2 = i < str2.length ? str2[i] : '';
        
        if (char1 !== char2) {
            html1 += `<span style="background: #fecaca; padding: 0 2px; border-radius: 2px; font-weight: bold;">${char1 || '∅'}</span>`;
            html2 += `<span style="background: #fecaca; padding: 0 2px; border-radius: 2px; font-weight: bold;">${char2 || '∅'}</span>`;
        } else {
            html1 += char1;
            html2 += char2;
        }
    }
    
    return [html1, html2];
}

function displayCollisionResults(data) {
    const container = document.getElementById('collisionResultsContent');
    const comparisonEl = document.getElementById('inputComparison');
    
    // Get input data from first result (all results have same input)
    const input1 = data.results[0].data1;
    const input2 = data.results[0].data2;
    
    // Display input comparison
    const [highlightedInput1, highlightedInput2] = highlightDifferences(input1, input2);
    const similarity = data.input_similarity || calculateStringSimilarity(input1, input2);
    
    comparisonEl.innerHTML = `
        <div style="background: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: var(--shadow);">
            <h3 style="color: var(--primary); margin-bottom: 1rem;">
                <i class="fas fa-search"></i> So sánh Inputs
            </h3>
            <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center;">
                <div>
                    <div style="background: var(--light); padding: 1rem; border-radius: 0.5rem;">
                        <p style="font-weight: 600; margin-bottom: 0.5rem;">📝 Input 1:</p>
                        <code style="background: white; padding: 0.5rem; display: block; border-radius: 0.25rem; font-size: 1rem;">
                            ${highlightedInput1}
                        </code>
                        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--gray);">
                            Length: ${input1.length} characters
                        </p>
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="background: var(--light); padding: 1rem; border-radius: 50%; width: 80px; height: 80px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <strong style="font-size: 1.5rem; color: var(--primary);">${similarity}%</strong>
                        <span style="font-size: 0.75rem; color: var(--gray);">giống nhau</span>
                    </div>
                </div>
                <div>
                    <div style="background: var(--light); padding: 1rem; border-radius: 0.5rem;">
                        <p style="font-weight: 600; margin-bottom: 0.5rem;">📝 Input 2:</p>
                        <code style="background: white; padding: 0.5rem; display: block; border-radius: 0.25rem; font-size: 1rem;">
                            ${highlightedInput2}
                        </code>
                        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--gray);">
                            Length: ${input2.length} characters
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = '<h3 style="color: var(--primary); margin: 1.5rem 0 1rem 0;"><i class="fas fa-chart-bar"></i> Kết quả Hash (Tất cả algorithms):</h3>';

    data.results.forEach(result => {
        const card = document.createElement('div');
        
        // Calculate avalanche effect percentage (% of bits changed)
        const avalanchePercent = ((result.changed_bits / result.total_bits) * 100).toFixed(2);
        
        // Color based on avalanche quality
        let qualityColor = 'var(--success)';
        if (avalanchePercent < 40 || avalanchePercent > 60) {
            qualityColor = 'var(--warning)';
        }
        if (avalanchePercent < 35 || avalanchePercent > 65) {
            qualityColor = 'var(--danger)';
        }
        
        card.style.cssText = `
            background: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid ${qualityColor};
            box-shadow: var(--shadow);
        `;
        
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="color: ${qualityColor}; margin: 0;">${result.algorithm}</h3>
                <span style="background: ${qualityColor}; color: white; padding: 0.35rem 1rem; border-radius: 1rem; font-size: 0.875rem; font-weight: 600;">
                    ${result.avalanche_quality}
                </span>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div style="background: var(--light); padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <div style="font-size: 0.85rem; color: var(--gray); margin-bottom: 0.25rem;">Hash Similarity</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">
                        ${result.similarity}%
                    </div>
                    <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">giống nhau</div>
                </div>
                <div style="background: var(--light); padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <div style="font-size: 0.85rem; color: var(--gray); margin-bottom: 0.25rem;">Changed Bits</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: ${qualityColor};">
                        ${result.changed_bits}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">/ ${result.total_bits} bits</div>
                </div>
                <div style="background: var(--light); padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <div style="font-size: 0.85rem; color: var(--gray); margin-bottom: 0.25rem;">Avalanche Effect</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: ${qualityColor};">
                        ${avalanchePercent}%
                    </div>
                    <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">ideal: 50%</div>
                </div>
            </div>
            
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: var(--primary); font-weight: 600; padding: 0.5rem 0;">
                    <i class="fas fa-eye"></i> Xem Hash Details
                </summary>
                <div style="margin-top: 1rem;">
                    <div style="background: #e0f2fe; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                        <p style="font-weight: 600; margin-bottom: 0.5rem; color: var(--dark);">🔐 Hash của "${result.data1}":</p>
                        <code style="word-break: break-all; font-size: 0.75rem; display: block; background: white; padding: 0.5rem; border-radius: 0.25rem;">
                            ${result.hash1}
                        </code>
                    </div>
                    <div style="background: #fce7f3; padding: 1rem; border-radius: 0.5rem;">
                        <p style="font-weight: 600; margin-bottom: 0.5rem; color: var(--dark);">🔐 Hash của "${result.data2}":</p>
                        <code style="word-break: break-all; font-size: 0.75rem; display: block; background: white; padding: 0.5rem; border-radius: 0.25rem;">
                            ${result.hash2}
                        </code>
                    </div>
                </div>
            </details>
        `;
        
        container.appendChild(card);
    });
    
    // Add explanation based on results
    const avgAvalanche = data.results.reduce((sum, r) => sum + (r.changed_bits / r.total_bits * 100), 0) / data.results.length;
    const explanationCard = document.createElement('div');
    explanationCard.style.cssText = `
        background: linear-gradient(135deg, #d1fae522 0%, #a7f3d022 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--success);
        margin-top: 1.5rem;
    `;
    explanationCard.innerHTML = `
        <h3 style="color: var(--success); margin-bottom: 1rem;">
            <i class="fas fa-check-circle"></i> Kết luận
        </h3>
        <p style="margin-bottom: 0.5rem;">
            <strong>Input similarity:</strong> ${similarity}% giống nhau
            <span style="font-size: 0.9rem; color: var(--gray);"> (${input1.length} vs ${input2.length} chars)</span>
        </p>
        <p style="margin-bottom: 0.5rem;">
            <strong>Average avalanche effect:</strong> ${avgAvalanche.toFixed(2)}% bits thay đổi
        </p>
        <p style="margin-top: 1rem; padding: 1rem; background: white; border-radius: 0.5rem;">
            <i class="fas fa-lightbulb" style="color: var(--warning);"></i>
            <strong>Ý nghĩa:</strong> Mặc dù inputs ${similarity > 80 ? 'rất' : ''} giống nhau (${similarity}%), 
            nhưng hashes hoàn toàn khác nhau với ~${avgAvalanche.toFixed(0)}% bits thay đổi. 
            Đây chính là <strong>Avalanche Effect</strong> - đặc tính quan trọng đảm bảo tính bảo mật của hash functions!
        </p>
    `;
    container.appendChild(explanationCard);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('btn-custom')) {
        setCollisionScenario('custom');
    }
});
