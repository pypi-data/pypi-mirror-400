const fs = require('fs');

// Read interactions
const interactions = JSON.parse(fs.readFileSync('activity_tracker_data/member_interactions.json', 'utf8'));

// Read members
const members = JSON.parse(fs.readFileSync('activity_tracker_data/members.json', 'utf8'));

// Count interactions per member
const memberCounts = new Map();
interactions.forEach(i => {
  if (i.member_id) {
    memberCounts.set(i.member_id, (memberCounts.get(i.member_id) || 0) + 1);
  }
});

// Sort by count
const sorted = Array.from(memberCounts.entries()).sort((a, b) => b[1] - a[1]);

console.log('Top 5 members by interaction count:');
sorted.slice(0, 5).forEach(([id, count]) => {
  const member = members.find(m => m.id === id);
  const name = member ? `${member.first_name} ${member.last_name}` : 'Unknown';
  console.log(`${id}: ${count} interactions (${name})`);
});

// Get first member with most interactions
if (sorted.length > 0) {
  const topMemberId = sorted[0][0];
  const topMember = members.find(m => m.id === topMemberId);
  console.log('\nMember with most activity:', topMemberId);
  console.log('Member Details:', JSON.stringify(topMember, null, 2));
}
