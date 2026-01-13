use std::fmt;
use std::fmt::Debug;
use std::sync::{Arc, Mutex};

pub struct Event<T> {
    listeners: Mutex<Vec<Arc<dyn Fn(&T) + Send + Sync>>>,
}

impl<T> Debug for Event<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Event({} listeners)",
            self.listeners.lock().unwrap().len()
        )
    }
}

impl<T> Default for Event<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> Event<T> {
    pub fn new() -> Self {
        Self {
            listeners: Mutex::new(Vec::new()),
        }
    }

    pub fn subscribe<F>(&self, f: F)
    where
        F: Fn(&T) + 'static + Send + Sync,
    {
        self.listeners.lock().unwrap().push(Arc::new(f));
    }

    pub fn emit(&self, data: &T) {
        // Clone the Arc pointers so we don't hold the lock while invoking callbacks
        let listeners = self.listeners.lock().unwrap().clone();
        for listener in listeners.iter() {
            listener(data);
        }
    }
}
