const fs = require('fs');

// Activity weights as per specification
const ACTIVITY_WEIGHTS = {
  attendance: 3,
  volunteering: 5,
  donation: 4,
  prayer_request: 2,
  small_group: 3,
  event_registration: 2,
  content_engagement: 1
};

// Engagement level thresholds
const ENGAGEMENT_LEVELS = {
  highly_active: { min: 80, max: 100 },
  active: { min: 60, max: 79 },
  moderate: { min: 40, max: 59 },
  low: { min: 20, max: 39 },
  inactive: { min: 0, max: 19 }
};

// Read data
const interactions = JSON.parse(fs.readFileSync('activity_tracker_data/member_interactions.json', 'utf8'));
const members = JSON.parse(fs.readFileSync('activity_tracker_data/members.json', 'utf8'));

// Target member ID
const targetMemberId = '48d7bfe6-39ce-4b4f-a442-001671f035c9';
const member = members.find(m => m.id === targetMemberId);

if (!member) {
  console.error('Member not found!');
  process.exit(1);
}

// Filter interactions for this member
const memberInteractions = interactions.filter(i => i.member_id === targetMemberId);

console.log(`\nAnalyzing ${memberInteractions.length} interactions for ${member.first_name} ${member.last_name}...\n`);

// Initialize activity counters
const activityCounts = {
  attendance: 0,
  volunteering: 0,
  donation: 0,
  prayer_request: 0,
  small_group: 0,
  event_registration: 0,
  content_engagement: 0
};

// Categorize interactions
memberInteractions.forEach(interaction => {
  const type = interaction.interaction_type || interaction.activity_type || '';

  // Map interaction types to activity categories
  if (type.includes('rsvp') || type.includes('event')) {
    activityCounts.event_registration++;
  } else if (type.includes('prayer')) {
    activityCounts.prayer_request++;
  } else if (type.includes('bible_study') || type.includes('group')) {
    activityCounts.small_group++;
  } else if (type.includes('volunteer')) {
    activityCounts.volunteering++;
  } else if (type.includes('donation') || type.includes('giving')) {
    activityCounts.donation++;
  } else if (type.includes('attendance')) {
    activityCounts.attendance++;
  } else {
    // Default to content engagement for other types
    activityCounts.content_engagement++;
  }
});

// Calculate weighted score
let totalWeightedScore = 0;
Object.entries(activityCounts).forEach(([activity, count]) => {
  const weight = ACTIVITY_WEIGHTS[activity];
  const contribution = count * weight;
  totalWeightedScore += contribution;
  console.log(`${activity}: ${count} interactions × ${weight} points = ${contribution} points`);
});

// Normalize to 0-100 scale (cap at 100)
const normalizedScore = Math.min(totalWeightedScore, 100);

// Determine engagement level
let engagementLevel = 'inactive';
for (const [level, range] of Object.entries(ENGAGEMENT_LEVELS)) {
  if (normalizedScore >= range.min && normalizedScore <= range.max) {
    engagementLevel = level;
    break;
  }
}

console.log(`\nTotal Weighted Score: ${totalWeightedScore}`);
console.log(`Normalized Score (0-100): ${normalizedScore}/100`);
console.log(`Engagement Level: ${engagementLevel}`);

// Calculate monthly trends
const monthlyTrend = {};
memberInteractions.forEach(i => {
  const date = new Date(i.interaction_date || i.created_at);
  const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  monthlyTrend[monthKey] = (monthlyTrend[monthKey] || 0) + 1;
});

// Get last activity date
const sortedByDate = memberInteractions
  .filter(i => i.interaction_date || i.created_at)
  .sort((a, b) => new Date(b.interaction_date || b.created_at) - new Date(a.interaction_date || a.created_at));

const lastActivity = sortedByDate[0] ? new Date(sortedByDate[0].interaction_date || sortedByDate[0].created_at) : null;
const daysSinceLastActivity = lastActivity ? Math.floor((new Date() - lastActivity) / (1000 * 60 * 60 * 24)) : null;

// Device usage analysis
const deviceTypes = {};
memberInteractions.forEach(i => {
  const device = i.metadata?.device_type || 'unknown';
  deviceTypes[device] = (deviceTypes[device] || 0) + 1;
});

// Top activities by frequency
const activityTypeCounts = {};
memberInteractions.forEach(i => {
  const type = i.interaction_type || i.activity_type || 'unknown';
  activityTypeCounts[type] = (activityTypeCounts[type] || 0) + 1;
});

const topActivities = Object.entries(activityTypeCounts)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10);

console.log('\n\nTop 10 Activities by Frequency:');
topActivities.forEach(([activity, count]) => {
  console.log(`  ${activity}: ${count}`);
});

console.log('\n\nMonthly Trends:');
Object.entries(monthlyTrend).sort().forEach(([month, count]) => {
  console.log(`  ${month}: ${count} interactions`);
});

console.log('\n\nDevice Usage:');
Object.entries(deviceTypes).forEach(([device, count]) => {
  console.log(`  ${device}: ${count} interactions`);
});

console.log(`\n\nLast Activity: ${lastActivity ? lastActivity.toISOString() : 'N/A'}`);
console.log(`Days Since Last Activity: ${daysSinceLastActivity || 'N/A'}`);

// Generate comprehensive analysis data
const analysisData = {
  member_id: targetMemberId,
  member_name: `${member.first_name} ${member.last_name}`,
  member_email: member.email,
  member_since: member.member_since,
  growth_stage: member.growth_stage,
  total_interactions: memberInteractions.length,
  activity_breakdown: activityCounts,
  weighted_scores: {},
  total_weighted_score: totalWeightedScore,
  normalized_score: normalizedScore,
  engagement_level: engagementLevel,
  monthly_trends: monthlyTrend,
  last_activity_date: lastActivity ? lastActivity.toISOString() : null,
  days_since_last_activity: daysSinceLastActivity,
  device_usage: deviceTypes,
  top_activities: topActivities,
  risk_assessment: normalizedScore < 40 ? 'HIGH' : normalizedScore < 60 ? 'MODERATE' : 'LOW',
  retention_probability: normalizedScore < 40 ? 'LOW' : normalizedScore < 60 ? 'MODERATE' : 'HIGH'
};

// Save analysis data
fs.writeFileSync(
  'activity_tracker_data/analysis_result.json',
  JSON.stringify(analysisData, null, 2),
  'utf8'
);

console.log('\n\nAnalysis complete! Data saved to activity_tracker_data/analysis_result.json');
