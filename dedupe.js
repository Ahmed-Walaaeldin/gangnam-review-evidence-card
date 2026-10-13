/* Candidate triage only. Similar wording is not proof of a shared patient or source post. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.reviewDedupe = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const stop = new Set('a about after again all also an and are as at be because been but by for from had has have in into is it its later of on or overall patient reported result reviewer said same she that the their they this to was were while with would'.split(' '));
  const canonical = value => String(value).toLowerCase().normalize('NFKD').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
  function tokens(value) {
    return new Set(canonical(value).split(' ').filter(word => word.length > 2 && !stop.has(word)));
  }
  function similarity(left, right) {
    const a = tokens(left), b = tokens(right);
    if (!a.size || !b.size) return { score: 0, shared: [] };
    const shared = [...a].filter(word => b.has(word)).sort();
    return { score: shared.length / new Set([...a, ...b]).size, shared };
  }
  function compare(a, b) {
    const sameClinic = canonical(a.clinic) === canonical(b.clinic);
    const sameDate = a.date === b.date;
    const sameProcedure = canonical(a.procedure) === canonical(b.procedure);
    const match = similarity(a.summary, b.summary);
    const candidate = sameClinic && sameDate && sameProcedure && match.score >= 0.24;
    return { candidate, sameClinic, sameDate, sameProcedure, score: match.score, shared: match.shared };
  }
  function triage(reviews) {
    const pairs = [];
    for (let i = 0; i < reviews.length; i++) {
      for (let j = i + 1; j < reviews.length; j++) {
        const result = compare(reviews[i], reviews[j]);
        if (result.candidate) pairs.push({ left: reviews[i], right: reviews[j], ...result });
      }
    }
    return pairs.sort((a, b) => b.score - a.score);
  }
  return { compare, triage, similarity };
});
