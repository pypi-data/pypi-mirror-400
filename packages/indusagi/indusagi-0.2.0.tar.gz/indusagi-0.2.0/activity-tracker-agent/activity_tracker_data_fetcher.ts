/**
 * Activity Tracker Data Fetcher (TypeScript)
 * Mirrors the Python workflow: pulls members, interactions, and member activities
 * from Supabase, calculates engagement metrics, and writes JSON exports for
 * downstream storage/analysis.
 */
import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createClient } from '@supabase/supabase-js';
import type { SupabaseClient } from '@supabase/supabase-js';

type Member = {
  id: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  [key: string]: any;
};

type Interaction = {
  member_id?: string;
  interaction_type?: string;
  activity_type?: string;
  created_at?: string;
  interaction_date?: string;
  [key: string]: any;
};

type ActivityAnalysis = {
  total_activities: number;
  activity_breakdown: Record<string, number>;
  monthly_trend: Record<string, number>;
  most_active_days: Array<[string, number]>;
  activity_frequency: number;
};

type MemberAnalysis = Member & {
  engagement_score: number;
  engagement_level: string;
  total_activities: number;
  activity_breakdown: Record<string, number>;
  monthly_trend: Record<string, number>;
  most_active_days: Array<[string, number]>;
  activity_frequency: number;
  last_activity_date: string | null;
  days_since_last_activity: number | null;
  ui_formatted: Record<string, any>;
};

const __filename = fileURLToPath(import.meta.url);

const DATA_DIR = 'activity_tracker_data';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  throw new Error('Missing SUPABASE_URL or SUPABASE_KEY environment variables');
}

const ACTIVITY_WEIGHTS: Record<string, number> = {
  attendance: 3,
  volunteering: 5,
  donation: 4,
  prayer_request: 2,
  small_group: 3,
  event_registration: 2,
  content_engagement: 1
};

const ENGAGEMENT_LEVELS: Record<
  string,
  { min_score: number; description: string; color: string }
> = {
  highly_active: { min_score: 80, description: 'Very engaged member', color: 'green' },
  active: { min_score: 60, description: 'Regularly engaged', color: 'blue' },
  moderate: { min_score: 40, description: 'Somewhat engaged', color: 'yellow' },
  low: { min_score: 20, description: 'Minimal engagement', color: 'orange' },
  inactive: { min_score: 0, description: 'No recent activity', color: 'red' }
};

const supabase: SupabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);

function ensureOutputDirectory(): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

async function fetchMembers(memberId?: string, memberIds?: string[]): Promise<Member[]> {
  // Batch mode: filter by multiple member IDs
  if (memberIds && memberIds.length > 0) {
    const { data, error } = await supabase.from('members').select('*').in('id', memberIds);
    if (error) {
      console.error('Error fetching members (batch)', error.message);
      return [];
    }
    return data || [];
  }

  // Single member mode: filter by single member ID
  if (memberId) {
    const { data, error } = await supabase.from('members').select('*').eq('id', memberId);
    if (error) {
      console.error('Error fetching member', error.message);
      return [];
    }
    return data || [];
  }

  // All members mode: no filter
  const { data, error } = await supabase.from('members').select('*');
  if (error) {
    console.error('Error fetching members', error.message);
    return [];
  }
  return data || [];
}

async function fetchMemberInteractions(memberId?: string, memberIds?: string[]): Promise<Interaction[]> {
  const query = supabase.from('member_interactions').select('*');

  // Batch mode: filter by multiple member IDs
  if (memberIds && memberIds.length > 0) {
    const { data, error } = await query.in('member_id', memberIds);
    if (error) {
      console.error('Error fetching member interactions (batch)', error.message);
      return [];
    }
    return data || [];
  }

  // Single member mode or all members
  const { data, error } = memberId ? await query.eq('member_id', memberId) : await query;
  if (error) {
    console.error('Error fetching member interactions', error.message);
    return [];
  }
  return data || [];
}

async function fetchMemberActivities(memberId?: string, memberIds?: string[]): Promise<Interaction[]> {
  const query = supabase.from('member_activities').select('*');

  // Batch mode: filter by multiple member IDs
  if (memberIds && memberIds.length > 0) {
    const { data, error } = await query.in('member_id', memberIds);
    if (error) {
      console.error('Error fetching member activities (batch)', error.message);
      return [];
    }
    return data || [];
  }

  // Single member mode or all members
  const { data, error } = memberId ? await query.eq('member_id', memberId) : await query;
  if (error) {
    console.error('Error fetching member activities', error.message);
    return [];
  }
  return data || [];
}

function toDate(value?: string | null): Date | null {
  if (!value) return null;
  try {
    return new Date(value.replace('Z', '+00:00'));
  } catch {
    return null;
  }
}

function calculateEngagementScore(activities: Interaction[], daysLookback = 90): number {
  const cutoff = Date.now() - daysLookback * 24 * 60 * 60 * 1000;
  let totalScore = 0;

  for (const activity of activities) {
    const dateField = activity.interaction_date || activity.created_at;
    const activityDate = toDate(dateField);
    if (!activityDate || activityDate.getTime() < cutoff) continue;

    const activityType = activity.interaction_type || activity.activity_type || '';
    const weight = ACTIVITY_WEIGHTS[activityType] ?? 1;
    totalScore += weight;
  }

  return Math.min(totalScore, 100);
}

function getEngagementLevel(score: number): string {
  const entries = Object.entries(ENGAGEMENT_LEVELS).sort(
    (a, b) => b[1].min_score - a[1].min_score
  );
  for (const [level, cfg] of entries) {
    if (score >= cfg.min_score) return level;
  }
  return 'inactive';
}

function analyzeActivityPatterns(activities: Interaction[]): ActivityAnalysis {
  if (!activities.length) {
    return {
      total_activities: 0,
      activity_breakdown: {},
      monthly_trend: {},
      most_active_days: [],
      activity_frequency: 0
    };
  }

  const activityBreakdown: Record<string, number> = {};
  const monthlyTrend: Record<string, number> = {};
  const dailyCounts: Record<string, number> = {};

  for (const activity of activities) {
    const activityType = activity.interaction_type || activity.activity_type || 'unknown';
    activityBreakdown[activityType] = (activityBreakdown[activityType] || 0) + 1;

    const dateField = activity.interaction_date || activity.created_at;
    const activityDate = toDate(dateField);
    if (!activityDate) continue;

    const monthKey = activityDate.toISOString().slice(0, 7);
    monthlyTrend[monthKey] = (monthlyTrend[monthKey] || 0) + 1;

    const dayKey = activityDate.toLocaleDateString('en-US', { weekday: 'long' });
    dailyCounts[dayKey] = (dailyCounts[dayKey] || 0) + 1;
  }

  const mostActiveDays = Object.entries(dailyCounts).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const monthCount = Object.keys(monthlyTrend).length;
  const activityFrequency =
    monthCount > 0
      ? Number(
          (
            Object.values(monthlyTrend).reduce((sum, val) => sum + val, 0) / monthCount
          ).toFixed(2)
        )
      : 0;

  return {
    total_activities: activities.length,
    activity_breakdown: activityBreakdown,
    monthly_trend: monthlyTrend,
    most_active_days: mostActiveDays,
    activity_frequency: activityFrequency
  };
}

function generateRecommendations(memberData: {
  engagement_level: string;
  days_since_last_activity: number | null;
}): string[] {
  const recommendations: string[] = [];
  const { engagement_level: engagementLevel, days_since_last_activity: daysSinceLast } = memberData;

  if (engagementLevel === 'inactive') {
    recommendations.push('Schedule personal outreach call', 'Send re-engagement email campaign', 'Invite to upcoming events');
  } else if (engagementLevel === 'low') {
    recommendations.push('Offer volunteer opportunities', 'Invite to small group activities', 'Follow up on interests and preferences');
  } else if (engagementLevel === 'moderate') {
    recommendations.push('Encourage leadership development', 'Suggest additional ministry involvement');
  } else if (['active', 'highly_active'].includes(engagementLevel)) {
    recommendations.push('Consider for leadership roles', 'Invite to mentor newer members');
  }

  if (typeof daysSinceLast === 'number' && daysSinceLast > 30) {
    recommendations.push('Check in on member wellbeing');
  }

  return recommendations;
}

function formatUiData(memberData: MemberAnalysis): Record<string, any> {
  const engagementLevel = memberData.engagement_level;
  const engagementScore = memberData.engagement_score;
  const engagementMeta = ENGAGEMENT_LEVELS[engagementLevel] || { description: '', color: 'gray', min_score: 0 };

  return {
    member_id: memberData.id,
    name: `${memberData.first_name ?? ''} ${memberData.last_name ?? ''}`.trim(),
    email: memberData.email ?? '',
    engagement: {
      score: engagementScore,
      level: engagementLevel,
      description: engagementMeta.description,
      status_color: engagementMeta.color
    },
    activity_summary: {
      total_activities: memberData.total_activities,
      activity_breakdown: memberData.activity_breakdown,
      monthly_frequency: memberData.activity_frequency,
      most_active_days: memberData.most_active_days
    },
    trends: {
      monthly_activity: memberData.monthly_trend,
      last_activity: memberData.last_activity_date,
      days_since_last_activity: memberData.days_since_last_activity
    },
    recommendations: generateRecommendations(memberData),
    ui_components: {
      engagement_badge: {
        text: engagementLevel.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        color: engagementMeta.color,
        score_display: `${engagementScore}/100`
      },
      activity_chart_data: Object.entries(memberData.activity_breakdown).map(([name, value]) => ({
        name,
        value
      })),
      progress_indicator: {
        percentage: engagementScore,
        color: engagementScore >= 60 ? 'green' : engagementScore >= 40 ? 'orange' : 'red'
      }
    }
  };
}

function parseArgs(args: string[]): { memberId?: string; memberIds?: string[] } {
  // Single member mode: --member_id or --member-id
  const singleIdx = args.findIndex(a => a === '--member_id' || a === '--member-id');
  const memberId = singleIdx >= 0 && args[singleIdx + 1] ? args[singleIdx + 1] : undefined;

  // Batch mode: --member_ids or --member-ids
  const batchIdx = args.findIndex(a => a === '--member_ids' || a === '--member-ids');
  const memberIds = batchIdx >= 0 && args[batchIdx + 1]
    ? args[batchIdx + 1].split(',').map(s => s.trim()).filter(Boolean)
    : undefined;

  return { memberId, memberIds };
}

async function analyzeMemberActivities(memberId?: string, memberIds?: string[]): Promise<void> {
  console.log('='.repeat(60));
  console.log('ACTIVITY TRACKER DATA FETCHER (TS)');
  console.log('='.repeat(60));

  console.log('[DATA FETCHER] Starting data fetch');
  console.log(`[DATA FETCHER] Member filter: ${memberIds ? memberIds.join(', ') : (memberId || 'ALL')}`);
  console.log(`[DATA FETCHER] Query type: ${memberIds ? 'BATCH' : (memberId ? 'SINGLE' : 'FULL')}`);

  if (memberId) {
    console.log(`Fetching data for specific member: ${memberId}`);
  } else if (memberIds) {
    console.log(`Fetching data for ${memberIds.length} members (batch mode)`);
  } else {
    console.log('Fetching member interaction data from Supabase...');
  }

  ensureOutputDirectory();

  const members = await fetchMembers(memberId, memberIds);
  if (!members.length) {
    console.error(memberId ? `Member ${memberId} not found` : 'No members returned from Supabase');
    return;
  }
  console.log(`Found ${members.length} member(s)`);

  const interactions = await fetchMemberInteractions(memberId, memberIds);
  const memberActivitiesTable = await fetchMemberActivities(memberId, memberIds);
  console.log(`Found ${interactions.length} interactions`);
  console.log(`Found ${memberActivitiesTable.length} member_activities rows`);

  const memberInteractionsMap = new Map<string, Interaction[]>();
  for (const activity of interactions) {
    const id = activity.member_id;
    if (!id) continue;
    if (!memberInteractionsMap.has(id)) {
      memberInteractionsMap.set(id, []);
    }
    memberInteractionsMap.get(id)!.push(activity);
  }

  const analysisResults: MemberAnalysis[] = [];
  const engagementDistribution: Record<string, number> = {};
  const activityTypeDistribution: Record<string, number> = {};

  for (const activity of interactions) {
    const activityType = activity.interaction_type || activity.activity_type || 'unknown';
    activityTypeDistribution[activityType] = (activityTypeDistribution[activityType] || 0) + 1;
  }

  const uiFormatted: Record<string, any>[] = [];

  for (const member of members) {
    const id = member.id;
    const memberActivityList = memberInteractionsMap.get(id) || [];

    const engagementScore = calculateEngagementScore(memberActivityList);
    const engagementLevel = getEngagementLevel(engagementScore);
    engagementDistribution[engagementLevel] = (engagementDistribution[engagementLevel] || 0) + 1;

    const activityAnalysis = analyzeActivityPatterns(memberActivityList);

    let lastActivityDate: string | null = null;
    let daysSinceLast: number | null = null;
    if (memberActivityList.length) {
      const activitiesWithDates = memberActivityList.filter(
        (a) => a.interaction_date || a.created_at
      );
      if (activitiesWithDates.length) {
        const sorted = activitiesWithDates.sort((a, b) => {
          const aDate = toDate(a.interaction_date || a.created_at) ?? new Date(0);
          const bDate = toDate(b.interaction_date || b.created_at) ?? new Date(0);
          return bDate.getTime() - aDate.getTime();
        });
        const topDate = toDate(sorted[0].interaction_date || sorted[0].created_at);
        if (topDate) {
          lastActivityDate = topDate.toISOString();
          daysSinceLast = Math.floor((Date.now() - topDate.getTime()) / (1000 * 60 * 60 * 24));
        }
      }
    }

    const memberAnalysis: MemberAnalysis = {
      ...member,
      engagement_score: engagementScore,
      engagement_level: engagementLevel,
      total_activities: activityAnalysis.total_activities,
      activity_breakdown: activityAnalysis.activity_breakdown,
      monthly_trend: activityAnalysis.monthly_trend,
      most_active_days: activityAnalysis.most_active_days,
      activity_frequency: activityAnalysis.activity_frequency,
      last_activity_date: lastActivityDate,
      days_since_last_activity: daysSinceLast,
      ui_formatted: {} // placeholder, populated below
    };

    memberAnalysis.ui_formatted = formatUiData(memberAnalysis);

    analysisResults.push(memberAnalysis);
    uiFormatted.push(memberAnalysis.ui_formatted);
  }

  const totalActivities = interactions.length;
  const avgEngagement =
    analysisResults.length > 0
      ? Number(
          (
            analysisResults.reduce((sum, m) => sum + m.engagement_score, 0) /
            analysisResults.length
          ).toFixed(2)
        )
      : 0;

  const summary = {
    total_members: members.length,
    total_activities: totalActivities,
    average_engagement_score: avgEngagement,
    engagement_distribution: engagementDistribution,
    activity_type_distribution: activityTypeDistribution,
    analysis_date: new Date().toISOString(),
    high_engagement_members: analysisResults.filter((m) =>
      ['highly_active', 'active'].includes(m.engagement_level)
    ).length,
    at_risk_members: analysisResults.filter((m) => m.engagement_level === 'inactive').length,
    recommendations: {
      re_engagement_needed: analysisResults.filter((m) => m.engagement_level === 'inactive').length,
      leadership_candidates: analysisResults.filter((m) => m.engagement_level === 'highly_active')
        .length,
      pastoral_care_priority: analysisResults.filter(
        (m) => (m.days_since_last_activity ?? 0) > 60
      ).length
    }
  };

  fs.writeFileSync(path.join(DATA_DIR, 'members.json'), JSON.stringify(members, null, 2), 'utf8');
  fs.writeFileSync(
    path.join(DATA_DIR, 'member_interactions.json'),
    JSON.stringify(interactions, null, 2),
    'utf8'
  );
  fs.writeFileSync(
    path.join(DATA_DIR, 'member_activities.json'),
    JSON.stringify(memberActivitiesTable, null, 2),
    'utf8'
  );

  console.log('\nActivity Tracker Analysis Results:');
  console.log('='.repeat(40));
  console.log(`Total Members: ${summary.total_members}`);
  console.log(`Total Activities: ${summary.total_activities}`);
  console.log(`Average Engagement Score: ${summary.average_engagement_score}/100`);
  console.log(`High Engagement Members: ${summary.high_engagement_members}`);
  console.log(`At-Risk Members: ${summary.at_risk_members}`);

  console.log('\nEngagement Distribution:');
  for (const [level, count] of Object.entries(summary.engagement_distribution)) {
    const percentage =
      summary.total_members > 0 ? (count / summary.total_members) * 100 : 0;
    console.log(`  ${level.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}: ${count} (${percentage.toFixed(1)}%)`);
  }

  console.log('\nTop Activity Types:');
  const sortedActivities = Object.entries(activityTypeDistribution).sort((a, b) => b[1] - a[1]);
  for (const [activityType, count] of sortedActivities.slice(0, 5)) {
    console.log(`  ${activityType.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}: ${count}`);
  }

  console.log(`\nFiles saved to ${DATA_DIR}/ directory`);
  console.log('Analysis complete!');
}

const isDirectRun =
  process.argv[1] && path.resolve(process.argv[1]) === path.resolve(__filename);

if (isDirectRun) {
  const { memberId, memberIds } = parseArgs(process.argv.slice(2));
  analyzeMemberActivities(memberId, memberIds).catch((err) => {
    console.error('Activity tracker fetcher failed:', err);
    process.exitCode = 1;
  });
}

export { analyzeMemberActivities };

