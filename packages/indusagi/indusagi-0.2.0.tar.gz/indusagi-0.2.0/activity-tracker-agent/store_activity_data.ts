/**
 * Store Activity Tracker analysis results into Supabase (activity_tracker_member_analysis).
 * Reads JSON exports from activity_tracker_data, recomputes engagement metrics, and upserts
 * per-member records. Mirrors the Python store_activity_data.py workflow.
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

type Metrics = {
  engagement_score: number;
  engagement_level: string;
  activity_patterns: {
    total_activities: number;
    activity_breakdown: Record<string, number>;
    monthly_trend: Record<string, number>;
    most_active_days: Array<[string, number]>;
    activity_frequency: number;
  };
  last_activity_date: string | null;
  weeks_since_last: number | null;
};

const __filename = fileURLToPath(import.meta.url);

const DATA_DIR = 'activity_tracker_data';
const REPORT_PREFIX = 'activity_tracking_analysis_comprehensive_';
const REPORT_FALLBACK_PREFIX = 'activity_tracking_analysis_comprehensive_batch';

const ACTIVITY_WEIGHTS: Record<string, number> = {
  attendance: 3,
  volunteering: 5,
  donation: 4,
  prayer_request: 2,
  small_group: 3,
  event_registration: 2,
  content_engagement: 1
};

function loadJson<T>(filePath: string, fallback: T): T {
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw) as T;
  } catch (err: any) {
    console.warn(`[WARN] Failed to read ${filePath}: ${err?.message || err}`);
    return fallback;
  }
}

function loadDepthSummary(memberId: string): string | undefined {
  const candidates = [
    `${REPORT_PREFIX}${memberId}.md`,
    `${REPORT_PREFIX}${memberId}`,
    `${REPORT_FALLBACK_PREFIX}.md`,
    REPORT_FALLBACK_PREFIX
  ];

  for (const filename of candidates) {
    try {
      return fs.readFileSync(filename, 'utf8');
    } catch {
      continue;
    }
  }

  console.warn('[WARN] No depth summary markdown found for member:', memberId);
  return undefined;
}

function parseDate(record: Interaction): Date | null {
  const ts = record.interaction_date || record.created_at;
  if (!ts) return null;
  try {
    return new Date(ts.replace('Z', '+00:00'));
  } catch {
    return null;
  }
}

function computeMetrics(memberId: string, interactions: Interaction[]): Metrics {
  const memberInteractions = interactions.filter((i) => i.member_id === memberId);

  let totalScore = 0;
  const breakdown: Record<string, number> = {};
  const monthlyTrend: Record<string, number> = {};
  const dailyCounts: Record<string, number> = {};
  let lastActivityDt: Date | null = null;

  for (const activity of memberInteractions) {
    const activityType = activity.interaction_type || activity.activity_type || 'unknown';
    const weight = ACTIVITY_WEIGHTS[activityType] ?? 1;
    totalScore += weight;
    breakdown[activityType] = (breakdown[activityType] || 0) + 1;

    const dt = parseDate(activity);
    if (dt) {
      const monthKey = dt.toISOString().slice(0, 7);
      monthlyTrend[monthKey] = (monthlyTrend[monthKey] || 0) + 1;
      const dayKey = dt.toLocaleDateString('en-US', { weekday: 'long' });
      dailyCounts[dayKey] = (dailyCounts[dayKey] || 0) + 1;
      if (!lastActivityDt || dt > lastActivityDt) {
        lastActivityDt = dt;
      }
    }
  }

  const engagement_score = Math.min(totalScore, 100);
  const engagement_level =
    engagement_score >= 80
      ? 'highly_active'
      : engagement_score >= 60
        ? 'active'
        : engagement_score >= 40
          ? 'moderate'
          : engagement_score >= 20
            ? 'low'
            : 'inactive';

  const totalActivities = memberInteractions.length;
  const mostActiveDays = Object.entries(dailyCounts).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const monthCount = Object.keys(monthlyTrend).length;
  const activity_frequency =
    monthCount > 0
      ? Number(
          (
            Object.values(monthlyTrend).reduce((sum, val) => sum + val, 0) / monthCount
          ).toFixed(2)
        )
      : 0;

  const last_activity_date = lastActivityDt ? lastActivityDt.toISOString() : null;
  const weeks_since_last = lastActivityDt
    ? Math.floor((Date.now() - lastActivityDt.getTime()) / (1000 * 60 * 60 * 24 * 7))
    : null;

  return {
    engagement_score,
    engagement_level,
    activity_patterns: {
      total_activities: totalActivities,
      activity_breakdown: breakdown,
      monthly_trend: monthlyTrend,
      most_active_days: mostActiveDays,
      activity_frequency
    },
    last_activity_date,
    weeks_since_last
  };
}

function parseMemberIds(args: string[]): string[] {
  const ids: string[] = [];
  const singleIdx = args.findIndex((arg) => arg === '--member_id' || arg === '--member-id');
  if (singleIdx >= 0 && args[singleIdx + 1]) {
    ids.push(args[singleIdx + 1]);
  }

  const listIdx = args.findIndex((arg) => arg === '--member_ids' || arg === '--member-ids');
  if (listIdx >= 0 && args[listIdx + 1]) {
    ids.push(
      ...args[listIdx + 1]
        .split(',')
        .map((id) => id.trim())
        .filter(Boolean)
    );
  }

  return Array.from(new Set(ids));
}

async function main(): Promise<void> {
  const memberIds = parseMemberIds(process.argv.slice(2));
  if (!memberIds.length) {
    console.error('[ERROR] No member_id provided. Use --member_id <UUID> or --member_ids <uuid1,uuid2,...>.');
    process.exit(1);
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY;
  if (!supabaseUrl || !supabaseKey) {
    console.error('[ERROR] SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY are required.');
    process.exit(1);
  }

  const supabase: SupabaseClient = createClient(supabaseUrl, supabaseKey);

  const members = loadJson<Member[]>(path.join(DATA_DIR, 'members.json'), []);
  const interactions = loadJson<Interaction[]>(path.join(DATA_DIR, 'member_interactions.json'), []);
  const memberActivities = loadJson<Interaction[]>(path.join(DATA_DIR, 'member_activities.json'), []);

  if (!members.length) {
    console.error('[ERROR] No members found in activity_tracker_data/members.json; aborting.');
    process.exit(1);
  }

  const combinedInteractions = [...interactions, ...memberActivities];
  const membersById = members.reduce<Record<string, Member>>((acc, m) => {
    if (m.id) acc[m.id] = m;
    return acc;
  }, {});

  const missing = memberIds.filter((id) => !membersById[id]);
  if (missing.length) {
    console.warn('[WARN] Requested member IDs not found in members.json:', missing);
  }

  const scopedMembers = memberIds.map((id) => membersById[id]).filter(Boolean);
  if (!scopedMembers.length) {
    console.error('[ERROR] None of the requested member IDs were found; aborting.');
    process.exit(1);
  }

  for (const member of scopedMembers) {
    const memberId = member.id;
    if (!memberId) {
      console.warn('[WARN] Skipping member with missing id.');
      continue;
    }

    const metrics = computeMetrics(memberId, combinedInteractions);

    const record = {
      member_id: memberId,
      member_name: `${member.first_name ?? ''} ${member.last_name ?? ''}`.trim(),
      email: member.email,
      phone: member.phone,
      engagement_score: metrics.engagement_score,
      engagement_level: metrics.engagement_level,
      activity_patterns: metrics.activity_patterns,
      last_activity_date: metrics.last_activity_date,
      analysis_date: new Date().toISOString(),
      recommendations: 'See analysis report; auto-generated placeholder.',
      depth_summary: loadDepthSummary(memberId)
    };

    const { error } = await supabase
      .from('activity_tracker_member_analysis')
      .upsert(record, { onConflict: 'member_id' });

    if (error) {
      console.error(`[ERROR] Failed to upsert member ${memberId}:`, error.message);
      continue;
    }

    console.log(`[OK] Stored analysis for member ${memberId} (score=${metrics.engagement_score})`);
  }

  console.log('[DONE] Storage complete.');
}

const isDirectRun =
  process.argv[1] && path.resolve(process.argv[1]) === path.resolve(__filename);

if (isDirectRun) {
  main().catch((err) => {
    console.error('Activity tracker storage failed:', err);
    process.exit(1);
  });
}

export { main as storeActivityData };

