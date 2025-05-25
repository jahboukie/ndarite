// NDARite Frontend-Backend Integration Test
// This script tests the connection between frontend and backend

const API_BASE_URL = 'http://localhost:8001/api/v1';

async function testBackendConnection() {
    console.log('🧪 Testing NDARite Frontend-Backend Integration...\n');
    
    const tests = [
        {
            name: 'Backend Health Check',
            url: 'http://localhost:8001/health',
            method: 'GET'
        },
        {
            name: 'API Status Check',
            url: `${API_BASE_URL}/status`,
            method: 'GET'
        },
        {
            name: 'Templates Endpoint',
            url: `${API_BASE_URL}/templates/`,
            method: 'GET'
        },
        {
            name: 'Template Categories',
            url: `${API_BASE_URL}/templates/categories/`,
            method: 'GET'
        },
        {
            name: 'Document Generation',
            url: `${API_BASE_URL}/documents/generate`,
            method: 'POST'
        }
    ];
    
    let passedTests = 0;
    let totalTests = tests.length;
    
    for (const test of tests) {
        try {
            console.log(`🔄 Testing: ${test.name}`);
            
            const response = await fetch(test.url, {
                method: test.method,
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${test.name}: PASSED`);
                console.log(`   Status: ${response.status}`);
                console.log(`   Response: ${JSON.stringify(data).substring(0, 100)}...\n`);
                passedTests++;
            } else {
                console.log(`❌ ${test.name}: FAILED`);
                console.log(`   Status: ${response.status}`);
                console.log(`   Error: ${response.statusText}\n`);
            }
        } catch (error) {
            console.log(`❌ ${test.name}: ERROR`);
            console.log(`   Error: ${error.message}\n`);
        }
    }
    
    console.log('📊 Integration Test Results:');
    console.log(`   Passed: ${passedTests}/${totalTests}`);
    console.log(`   Success Rate: ${Math.round((passedTests/totalTests) * 100)}%`);
    
    if (passedTests === totalTests) {
        console.log('\n🎉 ALL TESTS PASSED! Frontend-Backend integration is working perfectly!');
    } else {
        console.log('\n⚠️  Some tests failed. Check the backend server and API endpoints.');
    }
}

// Run the test
testBackendConnection().catch(console.error);
